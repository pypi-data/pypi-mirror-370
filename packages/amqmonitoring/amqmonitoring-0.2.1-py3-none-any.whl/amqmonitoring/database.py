#!/usr/bin/env python3
"""
Database module for AMQP monitoring sessions and message storage
"""
import os
import json
import logging
import asyncio
import aiosqlite
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


class AMQMDatabase:
    """Database handler for AMQP monitoring sessions and messages."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database with optional custom path."""
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = self._get_default_db_path()
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_db_exists = False
        
    def _get_default_db_path(self) -> Path:
        """Get default database path based on platform."""
        if platform.system() == "Windows":
            app_data = os.environ.get('APPDATA', '')
            if app_data:
                base_path = Path(app_data) / "amqm"
            else:
                base_path = Path.home() / "amqm"
        else:
            base_path = Path.home() / ".amqm"
        
        return base_path / "amqm.db"
    
    async def initialize(self):
        """Initialize database schema."""
        if self._ensure_db_exists:
            return
            
        logger.info(f"Initializing database at: {self.db_path}")
        
        async with aiosqlite.connect(self.db_path) as db:
            # Create sessions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    host TEXT,
                    port INTEGER,
                    username TEXT,
                    trace_queue TEXT,
                    total_messages INTEGER DEFAULT 0,
                    exchanges_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create connection settings table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS connection_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT,
                    trace_queue TEXT DEFAULT 'trace',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP
                )
            """)
            
            # Create messages table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    exchange_name TEXT NOT NULL,
                    routing_key TEXT NOT NULL,
                    trace_type TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    content_type TEXT,
                    delivery_mode INTEGER,
                    headers TEXT,
                    body TEXT,
                    raw_body TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            # Create exchange statistics table  
            await db.execute("""
                CREATE TABLE IF NOT EXISTS exchange_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    exchange_name TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id),
                    UNIQUE(session_id, exchange_name)
                )
            """)
            
            # Create indexes for better performance
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session_exchange 
                ON messages (session_id, exchange_name)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session_routing_key 
                ON messages (session_id, exchange_name, routing_key)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                ON messages (timestamp DESC)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_start_time 
                ON sessions (start_time DESC)
            """)
            
            await db.commit()
            
        self._ensure_db_exists = True
        logger.info("Database schema initialized successfully")
    
    async def create_session(self, name: str, host: str, port: int, 
                           username: str, trace_queue: str = "trace") -> str:
        """Create a new monitoring session."""
        session_id = str(uuid4())
        start_time = datetime.now()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO sessions (id, name, start_time, host, port, username, trace_queue)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, name, start_time, host, port, username, trace_queue))
            await db.commit()
            
        logger.info(f"Created new session: {session_id} - {name}")
        return session_id
    
    async def end_session(self, session_id: str):
        """End a monitoring session."""
        end_time = datetime.now()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Update session end time
            await db.execute("""
                UPDATE sessions 
                SET end_time = ? 
                WHERE id = ?
            """, (end_time, session_id))
            
            # Update total message count and exchanges count
            cursor = await db.execute("""
                SELECT COUNT(*) as total_messages, COUNT(DISTINCT exchange_name) as exchanges_count
                FROM messages 
                WHERE session_id = ?
            """, (session_id,))
            
            result = await cursor.fetchone()
            if result:
                total_messages, exchanges_count = result
                await db.execute("""
                    UPDATE sessions 
                    SET total_messages = ?, exchanges_count = ?
                    WHERE id = ?
                """, (total_messages, exchanges_count, session_id))
            
            await db.commit()
            
        logger.info(f"Ended session: {session_id}")
    
    async def store_message(self, session_id: str, message_info: Dict):
        """Store a message in the database."""
        async with aiosqlite.connect(self.db_path) as db:
            # Store the message
            await db.execute("""
                INSERT INTO messages (
                    session_id, exchange_name, routing_key, trace_type, timestamp,
                    content_type, delivery_mode, headers, body, raw_body
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                message_info.get('exchange', ''),
                message_info.get('routing_key', ''),
                message_info.get('trace_type', ''),
                message_info.get('timestamp', ''),
                message_info.get('properties', {}).get('content_type'),
                message_info.get('properties', {}).get('delivery_mode'),
                json.dumps(message_info.get('properties', {}).get('headers', {})),
                json.dumps(message_info.get('body', {})),
                message_info.get('raw_body', '')
            ))
            
            # Update exchange statistics
            await db.execute("""
                INSERT OR REPLACE INTO exchange_stats (session_id, exchange_name, message_count, last_update)
                VALUES (?, ?, COALESCE((
                    SELECT message_count + 1 
                    FROM exchange_stats 
                    WHERE session_id = ? AND exchange_name = ?
                ), 1), ?)
            """, (
                session_id, 
                message_info.get('exchange', ''),
                session_id,
                message_info.get('exchange', ''),
                datetime.now()
            ))
            
            await db.commit()
    
    async def get_sessions(self, limit: int = 50) -> List[Dict]:
        """Get list of monitoring sessions."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, name, start_time, end_time, host, port, username, 
                       trace_queue, total_messages, exchanges_count
                FROM sessions 
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            
            rows = await cursor.fetchall()
            sessions = []
            for row in rows:
                sessions.append({
                    'id': row[0],
                    'name': row[1],
                    'start_time': row[2],
                    'end_time': row[3],
                    'host': row[4],
                    'port': row[5],
                    'username': row[6],
                    'trace_queue': row[7],
                    'total_messages': row[8] or 0,
                    'exchanges_count': row[9] or 0
                })
            
            return sessions
    
    async def get_session_messages(self, session_id: str, 
                                 exchange_name: str = None,
                                 routing_key: str = None,
                                 limit: int = 1000) -> List[Dict]:
        """Get messages from a session."""
        async with aiosqlite.connect(self.db_path) as db:
            query = """
                SELECT exchange_name, routing_key, trace_type, timestamp,
                       content_type, delivery_mode, headers, body, raw_body
                FROM messages 
                WHERE session_id = ?
            """
            params = [session_id]
            
            if exchange_name:
                query += " AND exchange_name = ?"
                params.append(exchange_name)
                
            if routing_key:
                query += " AND routing_key = ?"
                params.append(routing_key)
                
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            messages = []
            for row in rows:
                try:
                    headers = json.loads(row[6]) if row[6] else {}
                    body = json.loads(row[7]) if row[7] else {}
                except json.JSONDecodeError:
                    headers = {}
                    body = {}
                    
                messages.append({
                    'exchange': row[0],
                    'exchange_name': row[0],  # Include both for compatibility
                    'routing_key': row[1],
                    'trace_type': row[2],
                    'timestamp': row[3],
                    'properties': {
                        'content_type': row[4],
                        'delivery_mode': row[5],
                        'headers': headers
                    },
                    'body': body,
                    'raw_body': row[8]
                })
            
            return messages
    
    async def get_session_exchange_stats(self, session_id: str) -> Dict[str, int]:
        """Get exchange statistics for a session."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT exchange_name, message_count
                FROM exchange_stats
                WHERE session_id = ?
                ORDER BY message_count DESC
            """, (session_id,))
            
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}
    
    async def get_session_routing_keys(self, session_id: str, 
                                     exchange_name: str) -> List[str]:
        """Get routing keys for a session and exchange."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT DISTINCT routing_key
                FROM messages
                WHERE session_id = ? AND exchange_name = ?
                ORDER BY routing_key
            """, (session_id, exchange_name))
            
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def save_connection_settings(self, name: str, host: str, port: int,
                                     username: str, password: str = None,
                                     trace_queue: str = "trace"):
        """Save connection settings."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO connection_settings 
                (name, host, port, username, password, trace_queue, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, host, port, username, password, trace_queue, datetime.now()))
            await db.commit()
    
    async def get_connection_settings(self) -> List[Dict]:
        """Get saved connection settings."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT name, host, port, username, password, trace_queue, last_used
                FROM connection_settings
                ORDER BY last_used DESC
            """)
            
            rows = await cursor.fetchall()
            settings = []
            for row in rows:
                settings.append({
                    'name': row[0],
                    'host': row[1],
                    'port': row[2],
                    'username': row[3],
                    'password': row[4] or '',
                    'trace_queue': row[5],
                    'last_used': row[6]
                })
            
            return settings
    
    async def delete_session(self, session_id: str):
        """Delete a session and all its messages."""
        async with aiosqlite.connect(self.db_path) as db:
            # Delete messages first
            await db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            # Delete exchange stats
            await db.execute("DELETE FROM exchange_stats WHERE session_id = ?", (session_id,))
            # Delete session
            await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            await db.commit()
            
        logger.info(f"Deleted session: {session_id}")