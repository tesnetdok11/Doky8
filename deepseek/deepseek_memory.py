"""
DEEPSEEK MEMORY - Basis data reasoning AI
"""

import logging
import json
import pickle
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

class DeepSeekMemory:
    def __init__(self):
        self.memory_file = "learning_memory/deepseek_memory.pkl"
        self.reasoning_db = "learning_memory/reasoning_database.json"
        self.memory_data = {
            'market_patterns': {},
            'signal_outcomes': {},
            'ai_insights': [],
            'optimization_learning': {},
            'context_memory': {}
        }
        
    async def initialize(self):
        """Initialize DeepSeek memory"""
        logging.info("💾 INITIALIZING DEEPSEEK MEMORY...")
        await self._load_memory()
        
    async def _load_memory(self):
        """Load memory from disk"""
        try:
            if Path(self.memory_file).exists():
                with open(self.memory_file, 'rb') as f:
                    self.memory_data = pickle.load(f)
                logging.info("✅ DeepSeek memory loaded successfully")
            else:
                logging.info("📝 No existing memory found, starting fresh")
                
        except Exception as e:
            logging.error(f"❌ Memory load error: {e}")
            self.memory_data = {
                'market_patterns': {},
                'signal_outcomes': {},
                'ai_insights': [],
                'optimization_learning': {},
                'context_memory': {}
            }
            
    async def save_memory(self):
        """Save memory to disk"""
        try:
            Path("learning_memory").mkdir(exist_ok=True)
            
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.memory_data, f)
                
            # Also save to JSON for readability
            with open(self.reasoning_db, 'w') as f:
                json.dump(self.memory_data, f, indent=2, default=str)
                
            logging.info("💾 DeepSeek memory saved successfully")
            
        except Exception as e:
            logging.error(f"❌ Memory save error: {e}")
            
    async def store_market_pattern(self, pattern_data, pair, timeframe):
        """Store market pattern in memory"""
        try:
            pattern_key = f"{pair}_{timeframe}"
            timestamp = datetime.utcnow().isoformat()
            
            pattern_entry = {
                'pattern': pattern_data,
                'timestamp': timestamp,
                'pair': pair,
                'timeframe': timeframe,
                'pattern_id': f"pattern_{timestamp.replace(':', '-').replace('.', '-')}"
            }
            
            if pattern_key not in self.memory_data['market_patterns']:
                self.memory_data['market_patterns'][pattern_key] = []
                
            self.memory_data['market_patterns'][pattern_key].append(pattern_entry)
            
            # Keep only recent patterns
            if len(self.memory_data['market_patterns'][pattern_key]) > 100:
                self.memory_data['market_patterns'][pattern_key] = \
                    self.memory_data['market_patterns'][pattern_key][-100:]
                    
        except Exception as e:
            logging.error(f"❌ Market pattern storage error: {e}")
            
    async def store_signal_outcome(self, signal, outcome, actual_pnl=None):
        """Store signal outcome for learning"""
        try:
            pair = signal.get('pair', 'unknown')
            signal_id = signal.get('signal_id', 
                                 f"signal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
            
            outcome_entry = {
                'signal_id': signal_id,
                'signal_data': signal,
                'outcome': outcome,  # 'success', 'failure', 'neutral'
                'actual_pnl': actual_pnl,
                'timestamp': datetime.utcnow().isoformat(),
                'confidence_used': signal.get('adjusted_confidence', signal.get('confidence', 0))
            }
            
            if pair not in self.memory_data['signal_outcomes']:
                self.memory_data['signal_outcomes'][pair] = []
                
            self.memory_data['signal_outcomes'][pair].append(outcome_entry)
            
            # Keep manageable history
            if len(self.memory_data['signal_outcomes'][pair]) > 500:
                self.memory_data['signal_outcomes'][pair] = \
                    self.memory_data['signal_outcomes'][pair][-500:]
                    
        except Exception as e:
            logging.error(f"❌ Signal outcome storage error: {e}")
            
    async def store_ai_insight(self, insight_data, insight_type):
        """Store AI-generated insights"""
        try:
            insight_entry = {
                'insight': insight_data,
                'type': insight_type,
                'timestamp': datetime.utcnow().isoformat(),
                'insight_id': f"insight_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            }
            
            self.memory_data['ai_insights'].append(insight_entry)
            
            # Keep only recent insights
            if len(self.memory_data['ai_insights']) > 1000:
                self.memory_data['ai_insights'] = self.memory_data['ai_insights'][-1000:]
                
        except Exception as e:
            logging.error(f"❌ AI insight storage error: {e}")
            
    async def get_signal_success_rate(self, pair, lookback_days=30):
        """Get success rate for signals of a specific pair"""
        try:
            if pair not in self.memory_data['signal_outcomes']:
                return 0.5  # Default to 50% if no data
                
            outcomes = self.memory_data['signal_outcomes'][pair]
            recent_outcomes = [
                outcome for outcome in outcomes
                if self._is_recent(outcome['timestamp'], lookback_days)
            ]
            
            if not recent_outcomes:
                return 0.5
                
            successful = len([o for o in recent_outcomes if o['outcome'] == 'success'])
            total = len(recent_outcomes)
            
            return successful / total if total > 0 else 0.5
            
        except Exception as e:
            logging.error(f"❌ Success rate calculation error: {e}")
            return 0.5
            
    async def get_confidence_calibration(self, pair, lookback_days=30):
        """Get confidence calibration data"""
        try:
            if pair not in self.memory_data['signal_outcomes']:
                return {'calibration_score': 0.5, 'overconfidence': 0}
                
            outcomes = self.memory_data['signal_outcomes'][pair]
            recent_outcomes = [
                outcome for outcome in outcomes
                if self._is_recent(outcome['timestamp'], lookback_days)
            ]
            
            if not recent_outcomes:
                return {'calibration_score': 0.5, 'overconfidence': 0}
                
            # Calculate calibration
            confidence_diffs = []
            for outcome in recent_outcomes:
                confidence = outcome['confidence_used']
                success = 1 if outcome['outcome'] == 'success' else 0
                confidence_diffs.append(abs(confidence - success))
                
            avg_diff = sum(confidence_diffs) / len(confidence_diffs)
            calibration_score = 1 - avg_diff  # 1 = perfect calibration
            
            # Calculate overconfidence
            overconfidence = len([d for d in confidence_diffs if d > 0.2]) / len(confidence_diffs)
            
            return {
                'calibration_score': calibration_score,
                'overconfidence': overconfidence,
                'sample_size': len(recent_outcomes)
            }
            
        except Exception as e:
            logging.error(f"❌ Confidence calibration error: {e}")
            return {'calibration_score': 0.5, 'overconfidence': 0}
            
    async def find_similar_patterns(self, current_pattern, pair, timeframe, max_results=5):
        """Find similar historical patterns"""
        try:
            pattern_key = f"{pair}_{timeframe}"
            if pattern_key not in self.memory_data['market_patterns']:
                return []
                
            historical_patterns = self.memory_data['market_patterns'][pattern_key]
            similarities = []
            
            for hist_pattern in historical_patterns[-100:]:  # Check recent patterns
                similarity = self._calculate_pattern_similarity(
                    current_pattern, hist_pattern['pattern']
                )
                
                if similarity > 0.6:  # Minimum similarity threshold
                    similarities.append({
                        'pattern': hist_pattern,
                        'similarity': similarity
                    })
                    
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:max_results]
            
        except Exception as e:
            logging.error(f"❌ Similar pattern search error: {e}")
            return []
            
    def _calculate_pattern_similarity(self, pattern1, pattern2):
        """Calculate similarity between two patterns"""
        try:
            # Simplified similarity calculation
            # In practice, this would use more sophisticated pattern matching
            common_keys = set(pattern1.keys()) & set(pattern2.keys())
            if not common_keys:
                return 0.0
                
            similarities = []
            for key in common_keys:
                if isinstance(pattern1[key], (int, float)) and isinstance(pattern2[key], (int, float)):
                    max_val = max(abs(pattern1[key]), abs(pattern2[key]), 1)
                    similarity = 1 - (abs(pattern1[key] - pattern2[key]) / max_val)
                    similarities.append(similarity)
                    
            return sum(similarities) / len(similarities) if similarities else 0.0
            
        except:
            return 0.0
            
    def _is_recent(self, timestamp, max_days):
        """Check if timestamp is within max_days"""
        try:
            record_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_diff = (datetime.utcnow() - record_time).total_seconds()
            return time_diff <= (max_days * 24 * 3600)
        except:
            return False
            
    async def get_memory_stats(self):
        """Get memory statistics"""
        stats = {
            'total_market_patterns': sum(len(patterns) for patterns in self.memory_data['market_patterns'].values()),
            'total_signal_outcomes': sum(len(outcomes) for outcomes in self.memory_data['signal_outcomes'].values()),
            'total_ai_insights': len(self.memory_data['ai_insights']),
            'pairs_with_patterns': len(self.memory_data['market_patterns']),
            'pairs_with_outcomes': len(self.memory_data['signal_outcomes'])
        }
        
        return stats
        
    async def cleanup_old_data(self, max_age_days=90):
        """Cleanup data older than max_age_days"""
        try:
            cleaned_count = 0
            
            # Clean market patterns
            for pattern_key in list(self.memory_data['market_patterns'].keys()):
                self.memory_data['market_patterns'][pattern_key] = [
                    p for p in self.memory_data['market_patterns'][pattern_key]
                    if self._is_recent(p['timestamp'], max_age_days)
                ]
                cleaned_count += len(self.memory_data['market_patterns'][pattern_key])
                
            # Clean signal outcomes
            for pair in list(self.memory_data['signal_outcomes'].keys()):
                self.memory_data['signal_outcomes'][pair] = [
                    o for o in self.memory_data['signal_outcomes'][pair]
                    if self._is_recent(o['timestamp'], max_age_days)
                ]
                
            # Clean AI insights
            self.memory_data['ai_insights'] = [
                i for i in self.memory_data['ai_insights']
                if self._is_recent(i['timestamp'], max_age_days)
            ]
            
            logging.info(f"🧹 Cleaned up data older than {max_age_days} days")
            
        except Exception as e:
            logging.error(f"❌ Memory cleanup error: {e}")
            
    async def cleanup(self):
        """Cleanup memory"""
        await self.save_memory()
        logging.info("🔒 DeepSeek memory cleanup completed")
