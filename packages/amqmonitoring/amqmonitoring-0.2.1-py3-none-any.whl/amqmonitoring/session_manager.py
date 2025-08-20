#!/usr/bin/env python3
"""
Session management for AMQP monitoring
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from .database import AMQMDatabase

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages monitoring sessions and database operations."""
    
    def __init__(self, database: AMQMDatabase):
        self.db = database
        self.current_session_id: Optional[str] = None
        self.current_session_name: Optional[str] = None
        
    async def initialize(self):
        """Initialize the session manager."""
        await self.db.initialize()
        
    async def start_session(self, name: str, host: str, port: int,
                          username: str, trace_queue: str = "trace") -> str:
        """Start a new monitoring session."""
        if self.current_session_id:
            await self.end_current_session()
            
        # Create unique session name if needed
        if not name:
            name = f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        self.current_session_id = await self.db.create_session(
            name, host, port, username, trace_queue
        )
        self.current_session_name = name
        
        logger.info(f"Started session: {self.current_session_name} ({self.current_session_id})")
        return self.current_session_id
        
    async def end_current_session(self):
        """End the current monitoring session."""
        if self.current_session_id:
            await self.db.end_session(self.current_session_id)
            logger.info(f"Ended session: {self.current_session_name}")
            self.current_session_id = None
            self.current_session_name = None
            
    async def store_message(self, message_info: Dict):
        """Store a message in the current session."""
        if not self.current_session_id:
            logger.warning("No active session - message not stored")
            return
            
        await self.db.store_message(self.current_session_id, message_info)
        
    async def get_sessions(self, limit: int = 50) -> List[Dict]:
        """Get list of all sessions."""
        return await self.db.get_sessions(limit)
        
    async def load_session(self, session_id: str) -> Dict:
        """Load a specific session's data."""
        sessions = await self.db.get_sessions(limit=1000)  # Get more to find specific one
        session = next((s for s in sessions if s['id'] == session_id), None)
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        # Load session messages and stats
        messages = await self.db.get_session_messages(session_id)
        exchange_stats = await self.db.get_session_exchange_stats(session_id)
        
        return {
            'session': session,
            'messages': messages,
            'exchange_stats': exchange_stats
        }
        
    async def get_session_exchange_messages(self, session_id: str, 
                                          exchange_name: str,
                                          limit: int = 1000) -> List[Dict]:
        """Get messages for a specific exchange in a session."""
        return await self.db.get_session_messages(
            session_id, exchange_name=exchange_name, limit=limit
        )
        
    async def get_session_routing_key_messages(self, session_id: str,
                                             exchange_name: str,
                                             routing_key: str,
                                             limit: int = 1000) -> List[Dict]:
        """Get messages for a specific routing key in a session."""
        return await self.db.get_session_messages(
            session_id, exchange_name=exchange_name, 
            routing_key=routing_key, limit=limit
        )
        
    async def get_session_routing_keys(self, session_id: str,
                                     exchange_name: str) -> List[str]:
        """Get routing keys for an exchange in a session."""
        return await self.db.get_session_routing_keys(session_id, exchange_name)
        
    async def save_connection_settings(self, name: str, host: str, port: int,
                                     username: str, password: str = None,
                                     trace_queue: str = "trace"):
        """Save connection settings for reuse."""
        await self.db.save_connection_settings(
            name, host, port, username, password, trace_queue
        )
        
    async def get_connection_settings(self) -> List[Dict]:
        """Get saved connection settings."""
        return await self.db.get_connection_settings()
        
    async def delete_session(self, session_id: str):
        """Delete a session and all its data."""
        await self.db.delete_session(session_id)
        
    def get_current_session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self.current_session_id
        
    def get_current_session_name(self) -> Optional[str]:
        """Get current session name."""
        return self.current_session_name
        
    def is_session_active(self) -> bool:
        """Check if there's an active session."""
        return self.current_session_id is not None