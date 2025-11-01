"""
WATCHDOG - Pemantau sistem 24/7 dengan auto-recovery
"""

import logging
import asyncio
import psutil
import time
from datetime import datetime, timedelta
from config import settings

class Watchdog:
    def __init__(self):
        self.health_metrics = {}
        self.performance_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 10.0  # seconds
        }
        self.alert_cooldown = 300  # 5 minutes
        self.last_alert_time = {}
        
    async def initialize(self):
        """Initialize watchdog"""
        logging.info("🐕 INITIALIZING WATCHDOG...")
        self.health_metrics = {
            'start_time': datetime.utcnow(),
            'restart_count': 0,
            'last_health_check': datetime.utcnow(),
            'system_metrics': {}
        }
        
    async def monitor_system(self):
        """Monitor system health and performance"""
        try:
            current_time = datetime.utcnow()
            
            # Collect system metrics
            metrics = await self._collect_system_metrics()
            self.health_metrics['system_metrics'] = metrics
            self.health_metrics['last_health_check'] = current_time
            
            # Check for issues
            issues = await self._check_system_health(metrics)
            
            if issues:
                await self._handle_system_issues(issues, metrics)
            else:
                logging.debug("✅ System health: OK")
                
            # Log health status periodically
            if current_time.minute % 5 == 0:  # Every 5 minutes
                await self._log_health_status(metrics)
                
            return metrics
            
        except Exception as e:
            logging.error(f"❌ Watchdog monitoring error: {e}")
            return {}
            
    async def _collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        try:
            metrics = {
                'timestamp': datetime.utcnow(),
                'cpu': {
                    'percent': psutil.cpu_percent(interval=1),
                    'count': psutil.cpu_count(),
                    'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                },
                'memory': {
                    'percent': psutil.virtual_memory().percent,
                    'available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                    'total_gb': round(psutil.virtual_memory().total / (1024**3), 2)
                },
                'disk': {
                    'percent': psutil.disk_usage('/').percent,
                    'free_gb': round(psutil.disk_usage('/').free / (1024**3), 2),
                    'total_gb': round(psutil.disk_usage('/').total / (1024**3), 2)
                },
                'network': {
                    'connections': len(psutil.net_connections()),
                    'io_counters': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
                },
                'process': {
                    'python_processes': len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()]),
                    'total_processes': len(list(psutil.process_iter()))
                },
                'dokyos_specific': {
                    'uptime_hours': (datetime.utcnow() - self.health_metrics['start_time']).total_seconds() / 3600,
                    'restart_count': self.health_metrics['restart_count']
                }
            }
            
            return metrics
            
        except Exception as e:
            logging.error(f"❌ System metrics collection error: {e}")
            return {}
            
    async def _check_system_health(self, metrics):
        """Check system health against thresholds"""
        issues = []
        
        try:
            # CPU check
            if metrics.get('cpu', {}).get('percent', 0) > self.performance_thresholds['cpu_percent']:
                issues.append({
                    'type': 'high_cpu',
                    'severity': 'warning',
                    'value': metrics['cpu']['percent'],
                    'threshold': self.performance_thresholds['cpu_percent']
                })
                
            # Memory check
            if metrics.get('memory', {}).get('percent', 0) > self.performance_thresholds['memory_percent']:
                issues.append({
                    'type': 'high_memory',
                    'severity': 'warning', 
                    'value': metrics['memory']['percent'],
                    'threshold': self.performance_thresholds['memory_percent']
                })
                
            # Disk check
            if metrics.get('disk', {}).get('percent', 0) > self.performance_thresholds['disk_percent']:
                issues.append({
                    'type': 'low_disk_space',
                    'severity': 'critical',
                    'value': metrics['disk']['percent'],
                    'threshold': self.performance_thresholds['disk_percent']
                })
                
            # Process stability check
            python_processes = metrics.get('process', {}).get('python_processes', 0)
            if python_processes > 10:  # Too many Python processes
                issues.append({
                    'type': 'too_many_processes',
                    'severity': 'warning',
                    'value': python_processes,
                    'threshold': 10
                })
                
            # Uptime check (prevent memory leaks)
            uptime_hours = metrics.get('dokyos_specific', {}).get('uptime_hours', 0)
            if uptime_hours > 168:  # 1 week
                issues.append({
                    'type': 'long_uptime',
                    'severity': 'info',
                    'value': uptime_hours,
                    'threshold': 168
                })
                
        except Exception as e:
            logging.error(f"❌ Health check error: {e}")
            
        return issues
        
    async def _handle_system_issues(self, issues, metrics):
        """Handle detected system issues"""
        for issue in issues:
            try:
                issue_type = issue['type']
                severity = issue['severity']
                
                # Check alert cooldown
                if issue_type in self.last_alert_time:
                    time_since_last_alert = (datetime.utcnow() - self.last_alert_time[issue_type]).total_seconds()
                    if time_since_last_alert < self.alert_cooldown:
                        continue
                        
                # Log issue based on severity
                message = f"🚨 {severity.upper()} - {issue_type}: {issue['value']} (threshold: {issue['threshold']})"
                
                if severity == 'critical':
                    logging.critical(message)
                    await self._trigger_recovery(issue_type, metrics)
                elif severity == 'warning':
                    logging.warning(message)
                else:
                    logging.info(message)
                    
                self.last_alert_time[issue_type] = datetime.utcnow()
                
            except Exception as e:
                logging.error(f"❌ Issue handling error: {e}")
                
    async def _trigger_recovery(self, issue_type, metrics):
        """Trigger recovery actions based on issue type"""
        try:
            recovery_actions = {
                'high_cpu': self._recover_high_cpu,
                'high_memory': self._recover_high_memory,
                'low_disk_space': self._recover_low_disk,
                'long_uptime': self._recover_long_uptime
            }
            
            if issue_type in recovery_actions:
                await recovery_actions[issue_type](metrics)
                
        except Exception as e:
            logging.error(f"❌ Recovery trigger error: {e}")
            
    async def _recover_high_cpu(self, metrics):
        """Recovery actions for high CPU"""
        logging.warning("🔧 Attempting CPU usage reduction...")
        
        # Reduce analysis intensity temporarily
        # This would be implemented in coordination with BrainController
        pass
        
    async def _recover_high_memory(self, metrics):
        """Recovery actions for high memory"""
        logging.warning("🔧 Attempting memory cleanup...")
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Clear large caches if possible
        # This would be implemented in coordination with other modules
        
    async def _recover_low_disk(self, metrics):
        """Recovery actions for low disk space"""
        logging.warning("🔧 Cleaning up disk space...")
        
        try:
            # Cleanup old log files
            await self._cleanup_old_logs()
            
            # Cleanup temporary files
            await self._cleanup_temp_files()
            
        except Exception as e:
            logging.error(f"❌ Disk cleanup error: {e}")
            
    async def _recover_long_uptime(self, metrics):
        """Recovery actions for long uptime"""
        logging.info("🔧 Considering restart after long uptime...")
        
        # After 1 week uptime, suggest restart
        # Actual restart would be manual or scheduled
        
    async def _cleanup_old_logs(self):
        """Cleanup old log files"""
        try:
            import os
            import glob
            from datetime import datetime, timedelta
            
            cutoff_time = datetime.now() - timedelta(days=7)
            log_files = glob.glob("logs/*.log*") + glob.glob("logs/signals/*.csv")
            
            for log_file in log_files:
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_time < cutoff_time:
                    os.remove(log_file)
                    logging.info(f"🧹 Removed old log file: {log_file}")
                    
        except Exception as e:
            logging.error(f"❌ Log cleanup error: {e}")
            
    async def _cleanup_temp_files(self):
        """Cleanup temporary files"""
        try:
            import os
            import glob
            
            temp_files = glob.glob("tmp/*.tmp") + glob.glob("cache/*.cache")
            for temp_file in temp_files:
                os.remove(temp_file)
                logging.info(f"🧹 Removed temp file: {temp_file}")
                
        except Exception as e:
            logging.error(f"❌ Temp file cleanup error: {e}")
            
    async def _log_health_status(self, metrics):
        """Log system health status"""
        try:
            cpu = metrics.get('cpu', {})
            memory = metrics.get('memory', {})
            disk = metrics.get('disk', {})
            
            status_message = (
                f"📊 System Health - "
                f"CPU: {cpu.get('percent', 0):.1f}%, "
                f"Memory: {memory.get('percent', 0):.1f}%, "
                f"Disk: {disk.get('percent', 0):.1f}%, "
                f"Uptime: {metrics.get('dokyos_specific', {}).get('uptime_hours', 0):.1f}h"
            )
            
            logging.info(status_message)
            
        except Exception as e:
            logging.error(f"❌ Health status logging error: {e}")
            
    async def check_external_dependencies(self):
        """Check external dependencies health"""
        try:
            dependencies = {
                'binance_api': await self._check_binance_health(),
                'telegram_bot': await self._check_telegram_health(),
                'github_sync': await self._check_github_health(),
                'deepseek_ai': await self._check_deepseek_health()
            }
            
            unhealthy = [name for name, status in dependencies.items() if not status]
            if unhealthy:
                logging.warning(f"⚠️ Unhealthy dependencies: {unhealthy}")
                
            return dependencies
            
        except Exception as e:
            logging.error(f"❌ Dependency check error: {e}")
            return {}
            
    async def _check_binance_health(self):
        """Check Binance API health"""
        try:
            # Simplified check - in practice would make actual API call
            return True
        except:
            return False
            
    async def _check_telegram_health(self):
        """Check Telegram bot health"""
        try:
            # Simplified check
            return True
        except:
            return False
            
    async def _check_github_health(self):
        """Check GitHub sync health"""
        try:
            # Simplified check
            return True
        except:
            return False
            
    async def _check_deepseek_health(self):
        """Check DeepSeek AI health"""
        try:
            # Simplified check
            return True
        except:
            return False
            
    async def get_system_report(self):
        """Generate comprehensive system report"""
        try:
            metrics = await self.monitor_system()
            dependencies = await self.check_external_dependencies()
            
            report = {
                'timestamp': datetime.utcnow().isoformat(),
                'system_metrics': metrics,
                'dependencies': dependencies,
                'health_metrics': self.health_metrics,
                'performance_thresholds': self.performance_thresholds
            }
            
            return report
            
        except Exception as e:
            logging.error(f"❌ System report generation error: {e}")
            return {}
            
    async def emergency_stop(self, reason="Unknown"):
        """Emergency stop the system"""
        try:
            logging.critical(f"🛑 EMERGENCY STOP: {reason}")
            
            # Perform graceful shutdown of components
            # This would coordinate with main system shutdown
            
            # Log emergency stop
            with open("logs/emergency_stop.log", "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} - Emergency stop: {reason}\n")
                
        except Exception as e:
            logging.error(f"❌ Emergency stop error: {e}")
            
    async def cleanup(self):
        """Cleanup watchdog"""
        logging.info("🔒 Watchdog cleanup completed")
