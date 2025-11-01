#!/usr/bin/env python3
"""
DOKYOS MAIN KERNEL - Autonomous AI Trading System
24/7 Runtime Loop dengan Async Architecture
"""

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from config import settings
from core.brain_controller import BrainController
from integrations.telegram_ai import TelegramAI
from security.watchdog import Watchdog
from security.logger import setup_logging

class DokyOS:
    def __init__(self):
        self.setup_system()
        self.brain = BrainController()
        self.telegram = TelegramAI()
        self.watchdog = Watchdog()
        self.is_running = True
        self.start_time = None
        
    def setup_system(self):
        """Setup sistem dasar"""
        setup_logging()
        logging.info("🚀 DOKYOS INITIALIZING...")
        
        # Signal handlers untuk graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logging.info(f"🛑 Received signal {signum}, shutting down...")
        self.is_running = False
        
    async def startup(self):
        """Startup sequence - METHOD YANG DIBUTUHKAN"""
        logging.info("🔧 RUNNING STARTUP SEQUENCE...")
        self.start_time = datetime.now(timezone.utc)  # FIX: gunakan timezone-aware
        
        try:
            # Initialize components dengan error handling
            if not await self.brain.initialize():
                logging.error("❌ Brain controller initialization failed")
                return False
                
            if not await self.telegram.initialize():
                logging.warning("⚠️ Telegram initialization failed - continuing without Telegram")
                
            if not await self.watchdog.initialize():
                logging.warning("⚠️ Watchdog initialization failed")
                
            # Send startup message
            await self.telegram.send_message("🟢 DOKYOS STARTED - System Online 24/7")
            logging.info("✅ STARTUP SEQUENCE COMPLETED")
            return True
            
        except Exception as e:
            logging.error(f"❌ Startup sequence failed: {e}")
            return False
            
    async def runtime_loop(self):
        """Main 24/7 runtime loop"""
        cycle_count = 0
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_running:
            try:
                start_time = time.time()
                cycle_count += 1
                
                # Reset error counter on successful cycle
                consecutive_errors = 0
                
                logging.info(f"🔄 Runtime Cycle #{cycle_count}")
                
                # 1. Health check sebelum memproses
                if not await self._system_health_check():
                    logging.warning("⚠️ System health check failed, skipping cycle")
                    await asyncio.sleep(10)
                    continue
                    
                # 2. Fetch market data dengan timeout
                market_data = await asyncio.wait_for(
                    self.brain.fetch_market_data(), 
                    timeout=30.0
                )
                
                if not market_data:
                    logging.warning("⏸️ No market data, skipping analysis")
                    await asyncio.sleep(5)
                    continue
                    
                # 3. Analyze market dengan circuit breaker
                analysis_result = await self._safe_analyze_market(market_data)
                
                if not analysis_result:
                    continue
                    
                # 4. Generate signals dengan validation
                signals = await self.brain.generate_signals(analysis_result)
                
                # 5. Send notifications dengan rate limiting
                if signals:
                    await self._send_controlled_notifications(signals)
                
                # 6. Update learning memory
                await self.brain.update_learning_memory(signals)
                
                # 7. Watchdog check
                await self.watchdog.monitor_system()
                
                cycle_time = time.time() - start_time
                logging.info(f"✅ Cycle #{cycle_count} completed in {cycle_time:.2f}s")
                
                # Adaptive sleep based on performance
                sleep_time = max(1, 10 - cycle_time)  # Minimal 1 detik
                await asyncio.sleep(sleep_time)
                
            except asyncio.TimeoutError:
                consecutive_errors += 1
                logging.error(f"⏰ Cycle #{cycle_count} timeout")
                await self._handle_timeout(consecutive_errors)
                
            except Exception as e:
                consecutive_errors += 1
                logging.error(f"❌ Runtime error cycle #{cycle_count}: {e}")
                await self._handle_runtime_error(e, consecutive_errors, max_consecutive_errors)

    async def _system_health_check(self):
        """Comprehensive system health check"""
        try:
            # Check system resources
            import psutil
            if psutil.virtual_memory().percent > 90:
                logging.warning("🔄 High memory usage detected")
                return False
                
            if psutil.cpu_percent() > 85:
                logging.warning("🔄 High CPU usage detected")  
                return False
                
            # Check disk space
            if psutil.disk_usage('/').percent > 90:
                logging.error("💾 Critical disk space")
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"❌ Health check error: {e}")
            return True  # Continue anyway

    async def _safe_analyze_market(self, market_data):
        """Safe market analysis with circuit breaker"""
        try:
            return await asyncio.wait_for(
                self.brain.analyze_market(market_data),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            logging.error("⏰ Market analysis timeout")
            return None
        except Exception as e:
            logging.error(f"❌ Market analysis error: {e}")
            return None

    async def _send_controlled_notifications(self, signals):
        """Send notifications with rate limiting"""
        try:
            for signal in signals:
                await self.telegram.send_signals([signal])
                # Rate limit: 1 signal per 2 seconds
                await asyncio.sleep(2)
        except Exception as e:
            logging.error(f"❌ Notification error: {e}")

    async def _handle_timeout(self, consecutive_errors):
        """Handle timeout errors"""
        backoff_time = min(consecutive_errors * 10, 60)  # Max 60 seconds
        logging.warning(f"⏸️ Backing off for {backoff_time}s due to timeouts")
        await asyncio.sleep(backoff_time)

    async def _handle_runtime_error(self, error, consecutive_errors, max_errors):
        """Handle runtime errors with escalation"""
        if consecutive_errors >= max_errors:
            logging.critical(f"🚨 Too many consecutive errors ({consecutive_errors}), initiating emergency shutdown")
            await self.emergency_shutdown()
        else:
            backoff_time = min(consecutive_errors * 5, 30)  # Max 30 seconds
            logging.warning(f"⏸️ Backing off for {backoff_time}s due to errors")
            await asyncio.sleep(backoff_time)

    async def emergency_shutdown(self):
        """Emergency shutdown procedure"""
        logging.critical("🛑 EMERGENCY SHUTDOWN INITIATED")
        await self.telegram.send_message("🔴 DOKYOS EMERGENCY SHUTDOWN - Too many consecutive errors")
        self.is_running = False
        
    async def shutdown(self):
        """Shutdown sequence - METHOD YANG DIBUTUHKAN"""
        logging.info("🔧 RUNNING SHUTDOWN SEQUENCE...")
        
        try:
            # Calculate uptime
            if self.start_time:
                uptime = datetime.now(timezone.utc) - self.start_time  # FIX: timezone-aware
                uptime_str = str(uptime).split('.')[0]  # Remove microseconds
                logging.info(f"📊 Total uptime: {uptime_str}")
            
            # Send shutdown message
            await self.telegram.send_message("🔴 DOKYOS SHUTTING DOWN...")
            
            # Cleanup components
            await self.brain.cleanup()
            await self.telegram.cleanup()
            await self.watchdog.cleanup()
            
            logging.info("✅ DOKYOS SHUTDOWN COMPLETE")
            
        except Exception as e:
            logging.error(f"❌ Shutdown sequence error: {e}")

async def main():
    """Main entry point"""
    dokyos = DokyOS()
    
    try:
        if await dokyos.startup():
            await dokyos.runtime_loop()
        else:
            logging.error("❌ Startup failed, shutting down")
            
    except Exception as e:
        logging.critical(f"💥 CRITICAL ERROR: {e}")
        
    finally:
        await dokyos.shutdown()

if __name__ == "__main__":
    # Run the system
    asyncio.run(main())
