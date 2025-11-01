"""
LEARNING MEMORY - Dataset hasil pembelajaran
"""

import logging
import json
import pickle
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

class LearningMemory:
    def __init__(self):
        self.memory_file = "learning_memory/learning_data.pkl"
        self.performance_data = []
        
    async def initialize(self):
        """Initialize learning memory"""
        logging.info("🎓 INITIALIZING LEARNING MEMORY...")
        await self._load_memory()
        
    async def _load_memory(self):
        """Load learning memory from disk"""
        try:
            if Path(self.memory_file).exists():
                with open(self.memory_file, 'rb') as f:
                    self.performance_data = pickle.load(f)
                logging.info(f"✅ Learning memory loaded: {len(self.performance_data)} records")
            else:
                self.performance_data = []
                logging.info("📝 No existing learning memory found")
        except Exception as e:
            logging.error(f"❌ Learning memory load error: {e}")
            self.performance_data = []
            
    async def save_memory(self):
        """Save learning memory to disk"""
        try:
            Path("learning_memory").mkdir(exist_ok=True)
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.performance_data, f)
            logging.info("💾 Learning memory saved")
        except Exception as e:
            logging.error(f"❌ Learning memory save error: {e}")
            
    async def record_trade_outcome(self, signal, outcome, pnl):
        """Record trade outcome for learning"""
        try:
            record = {
                'timestamp': datetime.utcnow(),
                'signal': signal,
                'outcome': outcome,  # 'win', 'loss', 'breakeven'
                'pnl': pnl,
                'market_conditions': await self._get_market_conditions()
            }
            
            self.performance_data.append(record)
            
            # Keep memory manageable
            if len(self.performance_data) > 10000:
                self.performance_data = self.performance_data[-10000:]
                
            # Auto-save periodically
            if len(self.performance_data) % 100 == 0:
                await self.save_memory()
                
        except Exception as e:
            logging.error(f"❌ Trade outcome recording error: {e}")
            
    async def _get_market_conditions(self):
        """Get current market conditions for context"""
        # This would be implemented to capture market state
        return {
            'volatility': 'medium',
            'trend': 'neutral', 
            'volume': 'average'
        }
        
    async def get_performance_stats(self, days=30):
        """Get performance statistics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_data = [d for d in self.performance_data if d['timestamp'] > cutoff_date]
            
            if not recent_data:
                return {}
                
            wins = len([d for d in recent_data if d['outcome'] == 'win'])
            losses = len([d for d in recent_data if d['outcome'] == 'loss'])
            total_trades = len(recent_data)
            
            win_rate = wins / total_trades if total_trades > 0 else 0
            total_pnl = sum(d['pnl'] for d in recent_data)
            avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_pnl': avg_pnl,
                'period_days': days
            }
            
        except Exception as e:
            logging.error(f"❌ Performance stats error: {e}")
            return {}
            
    async def cleanup(self):
        """Cleanup learning memory"""
        await self.save_memory()
        logging.info("🔒 Learning memory cleanup completed")
