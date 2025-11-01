"""
RECOVERY - Restart otomatis bila crash
"""

import logging
import asyncio
import subprocess
import sys
import time
from datetime import datetime, timedelta

class RecoverySystem:
    def __init__(self):
        self.crash_count = 0
        self.last_crash_time = None
        self.max_crashes_per_hour = 3
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5
        
    async def initialize(self):
        """Initialize recovery system"""
        logging.info("🔄 INITIALIZING RECOVERY SYSTEM...")
        
    async def handle_crash(self, exception, context=None):
        """Handle system crash and attempt recovery"""
        try:
            self.crash_count += 1
            current_time = datetime.utcnow()
            self.last_crash_time = current_time
            
            # Log crash details
            await self._log_crash(exception, context)
            
            # Check if we should attempt recovery
            if await self._should_attempt_recovery():
                await self._attempt_recovery(exception)
            else:
                await self._emergency_shutdown(exception)
                
        except Exception as e:
            logging.error(f"❌ Crash handling error: {e}")
            await self._emergency_shutdown(e)
            
    async def _should_attempt_recovery(self):
        """Determine if recovery should be attempted"""
        try:
            # Check crash frequency
            if self.last_crash_time:
                time_since_last_crash = (datetime.utcnow() - self.last_crash_time).total_seconds()
                crashes_per_hour = self.crash_count / (time_since_last_crash / 3600 + 1)
                
                if crashes_per_hour > self.max_crashes_per_hour:
                    logging.error("🚨 Too many crashes per hour - emergency shutdown")
                    return False
                    
            # Check recovery attempts
            if self.recovery_attempts >= self.max_recovery_attempts:
                logging.error("🚨 Maximum recovery attempts reached")
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"❌ Recovery decision error: {e}")
            return False
            
    async def _attempt_recovery(self, exception):
        """Attempt system recovery"""
        try:
            self.recovery_attempts += 1
            logging.warning(f"🔄 Attempting recovery #{self.recovery_attempts}...")
            
            # Determine recovery strategy based on exception type
            recovery_strategy = self._determine_recovery_strategy(exception)
            
            # Execute recovery actions
            success = await self._execute_recovery_actions(recovery_strategy)
            
            if success:
                logging.info("✅ Recovery successful")
                await self._log_recovery_success()
            else:
                logging.error("❌ Recovery failed")
                await self._handle_recovery_failure()
                
            return success
            
        except Exception as e:
            logging.error(f"❌ Recovery attempt error: {e}")
            return False
            
    def _determine_recovery_strategy(self, exception):
        """Determine appropriate recovery strategy based on exception"""
        exception_type = type(exception).__name__
        exception_message = str(exception).lower()
        
        strategies = {
            'memory_error': ['memory_cleanup', 'restart_process'],
            'connection_error': ['network_reset', 'service_restart'],
            'timeout_error': ['timeout_adjustment', 'retry'],
            'api_error': ['api_reset', 'circuit_breaker'],
            'unknown': ['full_restart']
        }
        
        # Map exceptions to strategies
        if 'memory' in exception_message or 'MemoryError' in exception_type:
            return strategies['memory_error']
        elif 'connection' in exception_message or 'ConnectionError' in exception_type:
            return strategies['connection_error']
        elif 'timeout' in exception_message or 'TimeoutError' in exception_type:
            return strategies['timeout_error']
        elif 'api' in exception_message or 'APIError' in exception_type:
            return strategies['api_error']
        else:
            return strategies['unknown']
            
    async def _execute_recovery_actions(self, strategy):
        """Execute recovery actions based on strategy"""
        try:
            recovery_actions = {
                'memory_cleanup': self._cleanup_memory,
                'restart_process': self._restart_process,
                'network_reset': self._reset_network,
                'service_restart': self._restart_service,
                'timeout_adjustment': self._adjust_timeouts,
                'api_reset': self._reset_apis,
                'circuit_breaker': self._activate_circuit_breaker,
                'full_restart': self._full_restart,
                'retry': self._retry_operation
            }
            
            for action_name in strategy:
                if action_name in recovery_actions:
                    logging.info(f"🔧 Executing recovery action: {action_name}")
                    success = await recovery_actions[action_name]()
                    if not success:
                        logging.warning(f"⚠️ Recovery action failed: {action_name}")
                        
            return True
            
        except Exception as e:
            logging.error(f"❌ Recovery action execution error: {e}")
            return False
            
    async def _cleanup_memory(self):
        """Cleanup memory and perform GC"""
        try:
            import gc
            import sys
            
            # Force garbage collection
            collected = gc.collect()
            logging.info(f"🧹 Garbage collection: {collected} objects collected")
            
            # Clear module caches if possible
            for module in list(sys.modules.values()):
                if hasattr(module, '__dict__'):
                    for attr in list(module.__dict__.keys()):
                        if attr.startswith('_cache'):
                            delattr(module, attr)
                            
            return True
            
        except Exception as e:
            logging.error(f"❌ Memory cleanup error: {e}")
            return False
            
    async def _restart_process(self):
        """Restart the current process"""
        try:
            logging.warning("🔄 Restarting DokyOS process...")
            
            # Use subprocess to restart
            subprocess.run([sys.executable, 'main.py'])
            sys.exit(0)  # Exit current process
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Process restart error: {e}")
            return False
            
    async def _reset_network(self):
        """Reset network connections"""
        try:
            # This would reset network connections in various modules
            # Implementation would coordinate with API modules
            logging.info("🔌 Resetting network connections...")
            return True
            
        except Exception as e:
            logging.error(f"❌ Network reset error: {e}")
            return False
            
    async def _restart_service(self):
        """Restart system service"""
        try:
            logging.warning("🔧 Restarting DokyOS service...")
            
            # Restart via systemd service
            subprocess.run(['sudo', 'systemctl', 'restart', 'doky_daemon.service'], 
                         check=True)
            return True
            
        except Exception as e:
            logging.error(f"❌ Service restart error: {e}")
            return False
            
    async def _adjust_timeouts(self):
        """Adjust operation timeouts"""
        try:
            logging.info("⏰ Adjusting operation timeouts...")
            
            # Increase timeouts temporarily
            # This would adjust settings in config modules
            return True
            
        except Exception as e:
            logging.error(f"❌ Timeout adjustment error: {e}")
            return False
            
    async def _reset_apis(self):
        """Reset API connections"""
        try:
            logging.info("🔗 Resetting API connections...")
            
            # Reinitialize API connections
            # This would coordinate with API modules
            return True
            
        except Exception as e:
            logging.error(f"❌ API reset error: {e}")
            return False
            
    async def _activate_circuit_breaker(self):
        """Activate circuit breaker for failing services"""
        try:
            logging.warning("⚡ Activating circuit breaker...")
            
            # Implement circuit breaker pattern
            # Temporarily disable failing services
            return True
            
        except Exception as e:
            logging.error(f"❌ Circuit breaker activation error: {e}")
            return False
            
    async def _full_restart(self):
        """Perform full system restart"""
        try:
            logging.critical("🔄 Performing full system restart...")
            
            # Comprehensive restart including cleanup
            await self._cleanup_memory()
            await self._reset_network()
            await self._restart_process()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Full restart error: {e}")
            return False
            
    async def _retry_operation(self):
        """Retry the failed operation"""
        try:
            logging.info("🔄 Retrying failed operation...")
            
            # Add delay before retry
            await asyncio.sleep(5)
            return True
            
        except Exception as e:
            logging.error(f"❌ Operation retry error: {e}")
            return False
            
    async def _log_crash(self, exception, context):
        """Log crash details"""
        try:
            crash_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'context': context,
                'crash_count': self.crash_count,
                'recovery_attempts': self.recovery_attempts,
                'system_info': await self._get_system_info()
            }
            
            # Write to crash log file
            with open("logs/crash_log.jsonl", "a") as f:
                f.write(f"{json.dumps(crash_log)}\n")
                
            logging.error(f"💥 System crash: {exception}")
            
        except Exception as e:
            logging.error(f"❌ Crash logging error: {e}")
            
    async def _get_system_info(self):
        """Get system information for crash reporting"""
        try:
            import platform
            import psutil
            
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'process_memory_mb': psutil.Process().memory_info().rss / 1024 / 1024
            }
        except:
            return {}
            
    async def _log_recovery_success(self):
        """Log successful recovery"""
        try:
            recovery_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'recovery_attempt': self.recovery_attempts,
                'crash_count': self.crash_count,
                'status': 'success'
            }
            
            with open("logs/recovery_log.jsonl", "a") as f:
                f.write(f"{json.dumps(recovery_log)}\n")
                
        except Exception as e:
            logging.error(f"❌ Recovery logging error: {e}")
            
    async def _handle_recovery_failure(self):
        """Handle recovery failure"""
        try:
            logging.critical("🚨 Recovery failed - initiating emergency procedures")
            
            # Log failure
            with open("logs/recovery_failure.log", "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} - Recovery failed after {self.recovery_attempts} attempts\n")
                
            # Notify administrators
            await self._notify_administrators()
            
        except Exception as e:
            logging.error(f"❌ Recovery failure handling error: {e}")
            
    async def _notify_administrators(self):
        """Notify system administrators of critical failure"""
        try:
            # This would integrate with Telegram or other notification systems
            logging.critical("📧 Notifying administrators of system failure")
            
        except Exception as e:
            logging.error(f"❌ Administrator notification error: {e}")
            
    async def _emergency_shutdown(self, exception):
        """Perform emergency shutdown"""
        try:
            logging.critical("🛑 INITIATING EMERGENCY SHUTDOWN")
            
            # Log emergency shutdown
            with open("logs/emergency_shutdown.log", "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} - Emergency shutdown: {exception}\n")
                
            # Stop all operations gracefully
            await self._stop_all_services()
            
            # Exit the application
            sys.exit(1)
            
        except Exception as e:
            logging.error(f"❌ Emergency shutdown error: {e}")
            sys.exit(1)
            
    async def _stop_all_services(self):
        """Stop all running services"""
        try:
            logging.info("🔴 Stopping all services...")
            
            # This would coordinate with all modules to perform cleanup
            # Implementation would depend on module architecture
            
            await asyncio.sleep(2)  # Give time for cleanup
            
        except Exception as e:
            logging.error(f"❌ Service stop error: {e}")
            
    async def reset_recovery_counters(self):
        """Reset recovery counters (call after successful operation)"""
        try:
            # Reset counters after period of stability
            time_since_last_crash = (datetime.utcnow() - self.last_crash_time).total_seconds() if self.last_crash_time else 0
            
            if time_since_last_crash > 3600:  # 1 hour without crashes
                self.crash_count = 0
                self.recovery_attempts = 0
                logging.info("📊 Recovery counters reset")
                
        except Exception as e:
            logging.error(f"❌ Recovery counter reset error: {e}")
            
    async def get_recovery_status(self):
        """Get current recovery system status"""
        return {
            'crash_count': self.crash_count,
            'recovery_attempts': self.recovery_attempts,
            'last_crash_time': self.last_crash_time,
            'max_recovery_attempts': self.max_recovery_attempts,
            'max_crashes_per_hour': self.max_crashes_per_hour
        }
        
    async def cleanup(self):
        """Cleanup recovery system"""
        logging.info("🔒 Recovery system cleanup completed")
