#!/usr/bin/env python3
"""
RabbitMQ Exchange Monitor - Core monitoring logic
"""
import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Callable, Optional
from collections import defaultdict, deque
from datetime import datetime

import pika
from pika.exceptions import AMQPConnectionError
import aio_pika

logger = logging.getLogger(__name__)


class ExchangeMonitor:
    """Monitor RabbitMQ exchanges and track message statistics."""
    
    def __init__(self, host: str = None, port: int = None,
                 username: str = None, password: str = None,
                 trace_queue_name: str = None):
        self.host = host or os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = port or int(os.getenv('RABBITMQ_PORT', '5672'))
        self.username = username or os.getenv('RABBITMQ_USER', 'guest')
        self.password = password or os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.trace_queue_name = trace_queue_name or "trace"
        
        self.connection = None
        self.channel = None
        self.is_running = False
        self.monitoring_task = None
        self.consumer_tag = None
        
        # Statistics storage
        self.exchange_stats: Dict[str, int] = defaultdict(int)
        self.exchange_messages: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.routing_key_messages: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=1000))
        )
        self.last_update = time.time()
        
        # Callbacks for updates
        self.update_callbacks: List[Callable] = []
        
    def add_update_callback(self, callback: Callable):
        """Add callback function to be called when stats are updated."""
        self.update_callbacks.append(callback)
        
    async def connect(self) -> tuple[bool, str]:
        """Connect to RabbitMQ server asynchronously.
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        try:
            connection_url = (
                f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/"
            )
            self.connection = await aio_pika.connect_robust(
                connection_url,
                timeout=10,
                client_properties={"connection_name": "AMQ Monitor"}
            )
            self.channel = await self.connection.channel()
            
            # Enable tracing by declaring trace queue and binding to trace exchange
            logger.info(f"Declaring trace queue: {self.trace_queue_name}")
            queue = await self.channel.declare_queue(self.trace_queue_name, durable=True)
            
            # Bind the queue to the RabbitMQ trace exchange to receive all trace messages
            logger.info(
                f"Binding queue '{self.trace_queue_name}' to 'amq.rabbitmq.trace' "
                f"with routing key '#'"
            )
            await queue.bind("amq.rabbitmq.trace", routing_key="#")
            
            # Log queue creation
            logger.info(f"Queue '{self.trace_queue_name}' ready for trace messages")
            
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            return True, ""
            
        except aio_pika.exceptions.AMQPConnectionError as e:
            error_msg = f"Connection failed to {self.host}:{self.port} - {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except aio_pika.exceptions.ProbableAuthenticationError:
            error_msg = (
                f"Authentication failed for user '{self.username}' - Invalid credentials"
            )
            logger.error(error_msg)
            return False, error_msg
        except aio_pika.exceptions.AuthenticationError:
            error_msg = (
                f"Access denied for user '{self.username}' - Insufficient permissions"
            )
            logger.error(error_msg)
            return False, error_msg
        except OSError as e:
            error_details = str(e)
            if "Connection refused" in error_details:
                error_msg = (
                    f"Connection refused - RabbitMQ server not running on "
                    f"{self.host}:{self.port}"
                )
            elif ("Name or service not known" in error_details or
                  "nodename nor servname provided" in error_details):
                error_msg = f"Host not found - Cannot resolve hostname '{self.host}'"
            elif "Network is unreachable" in error_details:
                error_msg = f"Network unreachable - Cannot reach host '{self.host}'"
            elif "timeout" in error_details.lower():
                error_msg = (
                    f"Connection timeout - No response from {self.host}:{self.port}"
                )
            else:
                error_msg = (
                    f"Network error connecting to {self.host}:{self.port} - {error_details}"
                )
            logger.error(error_msg)
            return False, error_msg
        except ValueError as e:
            error_msg = f"Invalid connection parameters - {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error connecting to RabbitMQ - {str(e)}"
            logger.error(error_msg)
            return False, error_msg
            
    async def disconnect(self):
        """Disconnect from RabbitMQ server."""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")
            
    def get_exchange_list(self) -> List[str]:
        """Get list of current exchanges from RabbitMQ management API or trace data."""
        # In a real implementation, you might use the management API
        # For now, return exchanges we've seen in traces
        return list(self.exchange_stats.keys())
        
    async def process_trace_message(
        self, message: aio_pika.abc.AbstractIncomingMessage
    ):
        """Process a trace message and update statistics."""
        logger.info("🔥 RECEIVED TRACE MESSAGE!")
        try:
            message_body = message.body.decode('utf-8')
            
            # RabbitMQ trace messages are structured differently
            # The routing key contains information about the trace type and exchange
            routing_key = message.routing_key
            
            logger.info(f"📨 Processing trace message with routing key: {routing_key}")
            logger.info(f"📨 Message body length: {len(message_body)}")
            logger.info(f"📨 Message headers: {message.headers}")
                
            # Parse routing key: "publish.{exchange}" or "deliver.{queue}"
            if not routing_key or '.' not in routing_key:
                logger.warning(
                    f"⚠️ Skipping trace message with invalid routing key: {routing_key}"
                )
                return
                
            parts = routing_key.split('.', 1)
            trace_type = parts[0]  # "publish" or "deliver"
            target = parts[1] if len(parts) > 1 else "unknown"
            
            logger.info(f"📨 Trace type: {trace_type}, Target: {target}")
                
            # Process both publish and deliver traces for better visibility
            if trace_type not in ["publish", "deliver"]:
                logger.warning(f"⚠️ Skipping unknown trace type: {trace_type}")
                await message.ack()  # Still acknowledge unknown messages
                return
                
            # For publish traces, target is the exchange name
            # For deliver traces, target is the queue name but we still want to track it
            if trace_type == "publish":
                exchange_name = target if target else "(default)"
            else:  # deliver
                # For deliver traces, we might want to extract the exchange from headers
                exchange_name = f"[Queue: {target}]"
                
            # Try to parse the message body as JSON for additional info
            message_dict = {}
            try:
                message_dict = json.loads(message_body)
            except json.JSONDecodeError:
                # If not JSON, store as text
                message_dict = {"raw_content": message_body}
                
            # Extract additional info from headers
            original_routing_key = "unknown"
            if message.headers:
                original_routing_key = message.headers.get('routing_key', 'unknown')
                # Sometimes routing keys are in different header fields
                if original_routing_key == 'unknown':
                    routing_keys = message.headers.get('routing_keys')
                    if routing_keys:
                        original_routing_key = routing_keys[0]
                    else:
                        original_routing_key = 'unknown'
                
            # Update exchange statistics
            self.exchange_stats[exchange_name] += 1
            
            # Store detailed message information
            message_info = {
                'timestamp': datetime.now().isoformat(),
                'exchange': exchange_name,
                'routing_key': original_routing_key,
                'trace_type': trace_type,
                'body': message_dict,
                'properties': {
                    'content_type': message.content_type,
                    'delivery_mode': message.delivery_mode,
                    'headers': dict(message.headers) if message.headers else {}
                },
                'raw_body': message_body
            }
                
            # Store in exchange-specific message history
            self.exchange_messages[exchange_name].append(message_info)
            logger.info(
                f"💾 Stored message for exchange '{exchange_name}', "
                f"total messages: {len(self.exchange_messages[exchange_name])}"
            )
            
            # Store in routing key-specific history for hierarchical viewing
            self.routing_key_messages[exchange_name][original_routing_key].append(
                message_info
            )
            routing_key_count = len(
                self.routing_key_messages[exchange_name][original_routing_key]
            )
            logger.info(
                f"💾 Stored message for routing key '{original_routing_key}', "
                f"total: {routing_key_count}"
            )
                
            self.last_update = time.time()
            
            # Log trace message for debugging
            logger.info(
                f"✅ Processed trace: Exchange '{exchange_name}' "
                f"(Key: '{original_routing_key}') - Total: {self.exchange_stats[exchange_name]}"
            )
            logger.info(f"📊 Current stats: {dict(self.exchange_stats)}")
                
            # Notify callbacks with updated statistics
            for callback in self.update_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(exchange_name, self.exchange_stats[exchange_name])
                    else:
                        callback(exchange_name, self.exchange_stats[exchange_name])
                except Exception as callback_error:
                    logger.error(f"Error in update callback: {callback_error}")
            
            # Acknowledge the message after successful processing
            await message.ack()
            logger.debug("✅ Message acknowledged and marked for deletion")
                        
        except Exception as process_error:
            logger.error(f"💥 Error processing trace message: {process_error}")
            logger.debug(f"Message routing key: {message.routing_key}")
            logger.debug(f"Message headers: {message.headers if message else 'None'}")
            logger.debug(f"Message body: {message.body[:200]}...")  # First 200 chars
            
            # Reject the message on error (don't requeue to avoid infinite loops)
            try:
                await message.reject(requeue=False)
                logger.debug("❌ Message rejected and marked for deletion")
            except Exception as reject_error:
                logger.error(f"Failed to reject message: {reject_error}")
            
    async def start_monitoring(self) -> tuple[bool, str]:
        """Start monitoring exchanges asynchronously.
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        if not self.connection:
            error_msg = "Not connected to RabbitMQ. Call connect() first."
            logger.error(error_msg)
            return False, error_msg
            
        try:
            self.is_running = True
            
            # Set up consumer for trace queue directly in this method
            logger.info(f"🚀 Starting monitoring for queue '{self.trace_queue_name}'")
            queue = await self.channel.get_queue(self.trace_queue_name)
            logger.info(f"✅ Got queue object: {queue}")
            
            # Set up the consumer with manual acknowledgment and ensure it stays active
            logger.info("🔧 Setting up robust consumer with manual acknowledgment...")
            
            # Configure channel for better stability
            await self.channel.set_qos(
                prefetch_count=10  # Process up to 10 messages at once
            )
            
            # Set up the consumer with manual acknowledgment
            self.consumer_tag = await queue.consume(
                self.process_trace_message,
                no_ack=False,
                exclusive=False,  # Allow multiple consumers
                consumer_tag="amq_monitor_consumer"  # Named consumer for debugging
            )
            
            logger.info(f"✅ Consumer set up successfully with tag: {self.consumer_tag}")
            logger.info(
                f"🎯 Consumer is now active and waiting for messages on queue "
                f"'{self.trace_queue_name}'"
            )
            
            # Start the background monitoring task to keep the consumer alive
            self.monitoring_task = asyncio.create_task(self._keep_monitoring_alive())
            
            return True, ""
            
        except Exception as e:
            error_msg = f"Failed to start monitoring - {str(e)}"
            logger.error(error_msg)
            logger.exception("Full error details:")
            return False, error_msg
            
    async def _keep_monitoring_alive(self):
        """Keep the monitoring task alive and check connection health."""
        try:
            message_count = 0
            last_message_count = 0
            logger.info("🔄 Monitoring task started - keeping consumer alive")
            
            while self.is_running:
                await asyncio.sleep(10)  # Check every 10 seconds
                message_count += 1
                
                # Check connection health every 30 seconds
                if message_count % 3 == 0:  # Every 30 seconds
                    try:
                        # Check if connection and channel are still alive
                        if self.connection and self.connection.is_closed:
                            logger.warning("🚨 Connection closed, attempting to reconnect...")
                            self.is_running = False
                            break
                            
                        if self.channel and self.channel.is_closed:
                            logger.warning("🚨 Channel closed, attempting to reconnect...")
                            self.is_running = False
                            break
                            
                        # Log periodic health check
                        stats = dict(self.exchange_stats)
                        total_messages = sum(stats.values())
                        
                        # Check if we're still receiving messages
                        if (total_messages == last_message_count and 
                            message_count > 6):  # No new messages after 1 minute
                            logger.info(
                                f"⏸️ No new messages received in the last minute - "
                                f"Total: {total_messages}"
                            )
                        else:
                            logger.info(
                                f"✅ Connection healthy - {len(stats)} exchanges, "
                                f"{total_messages} total messages"
                            )
                            
                        last_message_count = total_messages
                        
                        if stats and message_count % 6 == 0:  # Every minute
                            logger.info(f"📊 Exchange stats: {stats}")
                            
                    except Exception as health_error:
                        logger.error(f"💥 Error during health check: {health_error}")
                    
        except asyncio.CancelledError:
            logger.info("🛑 Monitoring keep-alive task cancelled")
            raise
        except Exception as e:
            logger.error(f"💥 Error in monitoring keep-alive: {e}")
            logger.exception("Full error details:")
        finally:
            logger.info("🏁 Monitoring keep-alive finished")
            self.is_running = False
        
    async def stop_monitoring(self):
        """Stop monitoring exchanges."""
        self.is_running = False
        
        # Cancel the consumer first
        if self.consumer_tag and self.channel and not self.channel.is_closed:
            try:
                logger.info(f"🛑 Cancelling consumer with tag: {self.consumer_tag}")
                await self.channel.basic_cancel(self.consumer_tag)
                self.consumer_tag = None
            except Exception as e:
                logger.warning(f"Error cancelling consumer: {e}")
        
        # Then cancel the monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            
    def get_exchange_messages(self, exchange_name: str, limit: int = 100) -> List[dict]:
        """Get recent messages for a specific exchange."""
        messages = list(self.exchange_messages.get(exchange_name, []))
        return messages[-limit:] if limit else messages
        
    def get_exchange_routing_keys(self, exchange_name: str) -> List[str]:
        """Get all routing keys for a specific exchange."""
        return list(self.routing_key_messages.get(exchange_name, {}).keys())
        
    def get_routing_key_messages(
        self, exchange_name: str, routing_key: str, limit: int = 100
    ) -> List[dict]:
        """Get recent messages for a specific exchange and routing key."""
        messages = list(
            self.routing_key_messages.get(exchange_name, {}).get(routing_key, [])
        )
        return messages[-limit:] if limit else messages
        
    def get_all_stats(self) -> Dict[str, int]:
        """Get all exchange statistics."""
        return dict(self.exchange_stats)
        
    def reset_stats(self):
        """Reset all statistics."""
        self.exchange_stats.clear()
        self.exchange_messages.clear()
        self.routing_key_messages.clear()
        logger.info("Statistics reset")