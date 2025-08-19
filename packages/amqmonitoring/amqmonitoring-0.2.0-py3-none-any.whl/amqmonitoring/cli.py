#!/usr/bin/env python3
"""
CLI interface for RabbitMQ monitoring
"""
import time
import asyncio
import logging
from typing import Dict

from .monitor import ExchangeMonitor

logger = logging.getLogger(__name__)


class CLIInterface:
    """Command-line interface for RabbitMQ monitoring."""
    
    def __init__(self, monitor: ExchangeMonitor):
        self.monitor = monitor
        self.running = False
        
    def start(self):
        """Start the CLI monitoring interface."""
        try:
            asyncio.run(self._async_start())
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping monitor...")
            
    async def _async_start(self):
        """Async implementation of CLI start."""
        logger.info("🐰 RabbitMQ Exchange Monitor - CLI Mode")
        logger.info("=" * 50)
        logger.info(
            f"Connecting to RabbitMQ at {self.monitor.host}:{self.monitor.port}"
        )
        
        success, error_msg = await self.monitor.connect()
        if not success:
            logger.error(f"❌ Failed to connect to RabbitMQ: {error_msg}")
            return
            
        logger.info("✅ Connected to RabbitMQ")
        
        # Start monitoring
        monitor_success, monitor_error = await self.monitor.start_monitoring()
        if not monitor_success:
            logger.error(f"❌ Failed to start monitoring: {monitor_error}")
            return
            
        logger.info("📊 Monitoring started. Press Ctrl+C to stop.")
        logger.info("-" * 50)
        
        self.running = True
        last_stats = {}
        
        try:
            while self.running:
                current_stats = self.monitor.get_all_stats()
                
                # Only update display if stats changed
                if current_stats != last_stats:
                    self._display_stats(current_stats)
                    last_stats = current_stats.copy()
                    
                await asyncio.sleep(1)  # Update every second
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping monitor...")
            await self.stop()
            
    async def stop(self):
        """Stop the CLI monitoring."""
        self.running = False
        await self.monitor.stop_monitoring()
        await self.monitor.disconnect()
        logger.info("👋 Monitor stopped")
        
    def _display_stats(self, stats: Dict[str, int]):
        """Display current exchange statistics."""
        logger.info("🐰 RabbitMQ Exchange Monitor - CLI Mode")
        logger.info("=" * 50)
        logger.info(f"Last update: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total exchanges: {len(stats)}")
        logger.info("-" * 50)
        
        if not stats:
            logger.info("📭 No exchanges found yet...")
        else:
            logger.info(f"{'Exchange Name':<30} {'Message Count':>15}")
            logger.info("-" * 50)
            
            # Sort exchanges by message count (descending) then by name
            sorted_exchanges = sorted(
                stats.items(), key=lambda x: (-x[1], x[0])
            )
            
            for exchange_name, message_count in sorted_exchanges:
                # Truncate long exchange names
                if len(exchange_name) > 30:
                    display_name = exchange_name[:27] + "..."
                else:
                    display_name = exchange_name
                logger.info(f"{display_name:<30} {message_count:>15,}")
                
        # Show total statistics
        total_messages = sum(stats.values())
        logger.info("-" * 50)
        logger.info(
            f"Total: {len(stats)} exchanges, {total_messages:,} messages"
        )
        logger.info("Press Ctrl+C to stop monitoring")