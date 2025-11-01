# security/performance_monitor.py
import time
import psutil
from datetime import datetime, timedelta

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.performance_thresholds = {
            'max_memory_mb': 1024,
            'max_cpu_percent': 85,
            'max_cycle_time': 10.0,
            'min_signals_per_hour': 2
        }
        
    async def initialize(self):
        logging.info("📊 Performance monitor initialized")
        
    async def record_cycle_metrics(self, cycle_time, signals_generated, errors):
        """Record metrics for each cycle"""
        metrics = {
            'timestamp': datetime.utcnow(),
            'cycle_time': cycle_time,
            'signals_generated': signals_generated,
            'errors': errors,
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,
            'cpu_percent': psutil.cpu_percent(),
            'system_load': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
        }
        
        self.metrics_history.append(metrics)
        
        # Keep only last 1000 records
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
            
        # Check performance thresholds
        await self._check_performance_thresholds(metrics)
        
    async def _check_performance_thresholds(self, metrics):
        """Check if performance metrics exceed thresholds"""
        alerts = []
        
        if metrics['memory_usage'] > self.performance_thresholds['max_memory_mb']:
            alerts.append(f"High memory usage: {metrics['memory_usage']:.1f}MB")
            
        if metrics['cpu_percent'] > self.performance_thresholds['max_cpu_percent']:
            alerts.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
            
        if metrics['cycle_time'] > self.performance_thresholds['max_cycle_time']:
            alerts.append(f"Slow cycle time: {metrics['cycle_time']:.2f}s")
            
        # Check signal rate (last hour)
        recent_signals = await self.get_signals_last_hour()
        if recent_signals < self.performance_thresholds['min_signals_per_hour']:
            alerts.append(f"Low signal rate: {recent_signals} signals/hour")
            
        if alerts:
            logging.warning(f"⚠️ Performance alerts: {', '.join(alerts)}")
            
    async def get_signals_last_hour(self):
        """Get number of signals in the last hour"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_cycles = [m for m in self.metrics_history if m['timestamp'] > one_hour_ago]
        return sum(m['signals_generated'] for m in recent_cycles)
        
    async def get_performance_report(self):
        """Generate performance report"""
        if not self.metrics_history:
            return {}
            
        recent_metrics = self.metrics_history[-100:]  # Last 100 cycles
        
        return {
            'avg_cycle_time': sum(m['cycle_time'] for m in recent_metrics) / len(recent_metrics),
            'avg_memory_usage': sum(m['memory_usage'] for m in recent_metrics) / len(recent_metrics),
            'avg_cpu_usage': sum(m['cpu_percent'] for m in recent_metrics) / len(recent_metrics),
            'total_signals_24h': await self.get_signals_last_hour() * 24,
            'error_rate': sum(m['errors'] for m in recent_metrics) / len(recent_metrics),
            'system_stability': await self.calculate_stability_score()
        }
        
    async def calculate_stability_score(self):
        """Calculate system stability score (0-100)"""
        if not self.metrics_history:
            return 100
            
        recent_metrics = self.metrics_history[-50:]
        
        # Factors affecting stability
        error_factor = 1 - (sum(m['errors'] for m in recent_metrics) / len(recent_metrics))
        memory_factor = 1 - min(1, recent_metrics[-1]['memory_usage'] / self.performance_thresholds['max_memory_mb'])
        cycle_time_factor = 1 - min(1, recent_metrics[-1]['cycle_time'] / self.performance_thresholds['max_cycle_time'])
        
        stability_score = (error_factor * 0.4 + memory_factor * 0.3 + cycle_time_factor * 0.3) * 100
        return max(0, min(100, stability_score))
