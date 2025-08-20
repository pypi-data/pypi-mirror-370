#!/usr/bin/env python3
"""
Test script to verify message display functionality
"""
import asyncio
import logging
from amqmonitoring.database import AMQMDatabase
from amqmonitoring.session_manager import SessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_message_display():
    """Test the message display functionality"""
    try:
        # Initialize database and session manager
        db = AMQMDatabase()
        await db.initialize()
        
        session_manager = SessionManager(db)
        
        # Get existing sessions
        sessions = await session_manager.get_sessions(limit=5)
        logger.info(f"Found {len(sessions)} sessions")
        
        if sessions:
            session = sessions[0]
            session_id = session['id']
            logger.info(f"Testing session: {session['name']} ({session_id})")
            
            # Load session data
            session_data = await session_manager.load_session(session_id)
            logger.info(f"Session has {len(session_data['messages'])} messages")
            logger.info(f"Exchange stats: {session_data['exchange_stats']}")
            
            # Test getting exchange messages
            if session_data['exchange_stats']:
                exchange_name = list(session_data['exchange_stats'].keys())[0]
                logger.info(f"Testing exchange: {exchange_name}")
                
                messages = await session_manager.get_session_exchange_messages(
                    session_id, exchange_name, limit=5
                )
                logger.info(f"Exchange {exchange_name} has {len(messages)} messages")
                
                # Test getting routing keys
                routing_keys = await session_manager.get_session_routing_keys(
                    session_id, exchange_name
                )
                logger.info(f"Exchange {exchange_name} has routing keys: {routing_keys}")
                
                # Test getting routing key messages
                if routing_keys:
                    routing_key = routing_keys[0]
                    rk_messages = await session_manager.get_session_routing_key_messages(
                        session_id, exchange_name, routing_key, limit=3
                    )
                    logger.info(f"Routing key {routing_key} has {len(rk_messages)} messages")
                    
                    if rk_messages:
                        logger.info("Sample message:")
                        sample_msg = rk_messages[0]
                        logger.info(f"  Timestamp: {sample_msg.get('timestamp')}")
                        logger.info(f"  Exchange: {sample_msg.get('exchange_name')}")
                        logger.info(f"  Routing Key: {sample_msg.get('routing_key')}")
                        logger.info(f"  Trace Type: {sample_msg.get('trace_type')}")
                        logger.info(f"  Body: {sample_msg.get('body', 'No body')}")
                
        else:
            logger.info("No sessions found in database")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_message_display())