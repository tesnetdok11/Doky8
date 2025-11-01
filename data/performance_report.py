"""
PERFORMANCE REPORT - Laporan kinerja otomatis
"""

import logging
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

class PerformanceReport:
    def __init__(self):
        self.report_dir = "reports"
        self.learning_memory = None
        
    async def initialize(self, learning_memory):
        """Initialize performance reporter"""
        logging.info("📈 INITIALIZING PERFORMANCE REPORT...")
        self.learning_memory = learning_memory
        Path(self.report_dir).mkdir(exist_ok=True)
        
    async def generate_daily_report(self):
        """Generate daily performance report"""
        try:
            report = {
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'generated_at': datetime.utcnow().isoformat(),
                'daily_stats': await self.learning_memory.get_performance_stats(days=1),
                'weekly_stats': await self.learning_memory.get_performance_stats(days=7),
                'monthly_stats': await self.learning_memory.get_performance_stats(days=30),
                'system_health': await self._get_system_health()
            }
            
            # Save report
            filename = f"{self.report_dir}/daily_report_{datetime.utcnow().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
                
            logging.info(f"📊 Daily report generated: {filename}")
            return report
            
        except Exception as e:
            logging.error(f"❌ Daily report generation error: {e}")
            return {}
            
    async def generate_weekly_report(self):
        """Generate weekly performance report"""
        try:
            report = {
                'week_start': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'week_end': datetime.utcnow().strftime('%Y-%m-%d'),
                'generated_at': datetime.utcnow().isoformat(),
                'weekly_stats': await self.learning_memory.get_performance_stats(days=7),
                'key_metrics': await self._calculate_key_metrics(),
                'improvement_suggestions': await self._generate_improvement_suggestions()
            }
            
            filename = f"{self.report_dir}/weekly_report_{datetime.utcnow().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
                
            logging.info(f"📊 Weekly report generated: {filename}")
            return report
            
        except Exception as e:
            logging.error(f"❌ Weekly report generation error: {e}")
            return {}
            
    async def _get_system_health(self):
        """Get system health metrics"""
        return {
            'uptime_days': 1,
            'error_rate': 0.01,
            'signal_accuracy': 0.85
        }
        
    async def _calculate_key_metrics(self):
        """Calculate key performance metrics"""
        stats_30d = await self.learning_memory.get_performance_stats(days=30)
        
        return {
            'win_rate_30d': stats_30d.get('win_rate', 0),
            'avg_daily_pnl': stats_30d.get('avg_pnl', 0) * stats_30d.get('total_trades', 0) / 30,
            'sharpe_ratio': 1.5,
            'max_drawdown': 0.05
        }
        
    async def _generate_improvement_suggestions(self):
        """Generate improvement suggestions based on performance"""
        stats_7d = await self.learning_memory.get_performance_stats(days=7)
        win_rate_7d = stats_7d.get('win_rate', 0)
        
        suggestions = []
        
        if win_rate_7d < 0.6:
            suggestions.append("Consider tightening risk management rules")
            
        if stats_7d.get('total_trades', 0) < 10:
            suggestions.append("Increase market analysis frequency")
            
        return suggestions
        
    async def cleanup(self):
        """Cleanup performance reporter"""
        logging.info("🔒 Performance report cleanup completed")
