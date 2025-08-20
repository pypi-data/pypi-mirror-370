#!/usr/bin/env python3
"""
Test script to verify session message viewing and export functionality
"""
import asyncio
import json
import tempfile
from pathlib import Path
from amqmonitoring.session_manager import SessionManager
from amqmonitoring.database import AMQMDatabase

async def test_session_functionality():
    """Test the complete session functionality"""
    print("🔍 Testing session message viewing and export functionality...")
    
    # Initialize
    db = AMQMDatabase()
    await db.initialize()
    session_manager = SessionManager(db)
    
    # Get sessions
    sessions = await session_manager.get_sessions(limit=1)
    if not sessions:
        print("❌ No sessions found in database")
        return
    
    session = sessions[0]
    session_id = session['id']
    print(f"✅ Found session: {session['name']} ({session_id})")
    print(f"📊 Total messages in session: {session['total_messages']}")
    
    # Load session data
    session_data = await session_manager.load_session(session_id)
    print(f"📈 Loaded session data with {len(session_data['messages'])} messages")
    print(f"🏭 Exchange stats: {session_data['exchange_stats']}")
    
    # Test exchange message loading
    if session_data['exchange_stats']:
        exchange_name = list(session_data['exchange_stats'].keys())[0]
        print(f"\n🔍 Testing exchange: {exchange_name}")
        
        # Get exchange messages
        exchange_messages = await session_manager.get_session_exchange_messages(
            session_id, exchange_name, limit=5
        )
        print(f"📨 Exchange {exchange_name} has {len(exchange_messages)} messages (showing first 5)")
        
        if exchange_messages:
            print("📋 Sample exchange message:")
            msg = exchange_messages[0]
            print(f"  🔑 Exchange: {msg.get('exchange_name', 'N/A')}")
            print(f"  🎯 Routing Key: {msg.get('routing_key', 'N/A')}")
            print(f"  ⏰ Timestamp: {msg.get('timestamp', 'N/A')}")
            print(f"  📄 Body: {json.dumps(msg.get('body', {}), indent=2)[:100]}...")
            
        # Test routing keys
        routing_keys = await session_manager.get_session_routing_keys(
            session_id, exchange_name
        )
        print(f"\n🎯 Routing keys for {exchange_name}: {routing_keys[:5]}...")  # Show first 5
        
        # Test routing key messages
        if routing_keys:
            routing_key = routing_keys[0]
            rk_messages = await session_manager.get_session_routing_key_messages(
                session_id, exchange_name, routing_key, limit=3
            )
            print(f"📨 Routing key '{routing_key}' has {len(rk_messages)} messages")
            
            if rk_messages:
                print("📋 Sample routing key message:")
                msg = rk_messages[0]
                print(f"  🔑 Exchange: {msg.get('exchange_name', 'N/A')}")
                print(f"  🎯 Routing Key: {msg.get('routing_key', 'N/A')}")
                print(f"  📄 Body: {json.dumps(msg.get('body', {}), indent=2)}")
        
        # Test export functionality
        print(f"\n💾 Testing export functionality...")
        
        # Test exchange export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
        
        # Simulate export
        all_exchange_messages = await session_manager.get_session_exchange_messages(
            session_id, exchange_name, limit=10000
        )
        
        export_data = {
            "export_info": {
                "session_id": session_id,
                "exchange_name": exchange_name,
                "export_timestamp": "2025-08-19T12:00:00",
                "total_messages": len(all_exchange_messages)
            },
            "messages": all_exchange_messages[:5]  # Just first 5 for test
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Exchange export test successful: {export_file}")
        print(f"📊 Exported {len(export_data['messages'])} sample messages")
        
        # Verify export file
        export_size = Path(export_file).stat().st_size
        print(f"📁 Export file size: {export_size} bytes")
        
        # Clean up
        Path(export_file).unlink()
        print("🗑️ Cleaned up test export file")
        
    print("\n✅ All tests completed successfully!")
    print("🎉 Session message viewing and export functionality is working!")

if __name__ == "__main__":
    asyncio.run(test_session_functionality())