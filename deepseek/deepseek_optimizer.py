"""
DEEPSEEK OPTIMIZER - Penyesuaian probabilitas sinyal
"""

import logging
import asyncio
from datetime import datetime
from config import settings

class DeepSeekOptimizer:
    def __init__(self):
        self.connector = None
        self.optimization_history = []
        
    async def initialize(self, connector):
        """Initialize DeepSeek optimizer"""
        logging.info("🎯 INITIALIZING DEEPSEEK OPTIMIZER...")
        self.connector = connector
        
    async def optimize_signals(self, signals, market_context, technical_analysis):
        """Optimize trading signals using AI"""
        if not signals:
            return []
            
        optimized_signals = []
        
        for signal in signals:
            try:
                optimized_signal = await self._optimize_single_signal(
                    signal, market_context, technical_analysis
                )
                optimized_signals.append(optimized_signal)
                
            except Exception as e:
                logging.error(f"❌ Signal optimization error: {e}")
                optimized_signals.append(signal)  # Use original signal on error
                
        return optimized_signals
        
    async def _optimize_single_signal(self, signal, market_context, technical_analysis):
        """Optimize single trading signal"""
        if not self.connector or not self.connector.enabled:
            return self._apply_basic_optimization(signal, technical_analysis)
            
        # Use AI for optimization
        ai_optimized = await self.connector.optimize_signal_confidence(
            signal, market_context
        )
        
        if ai_optimized and 'ai_confidence_boost' in ai_optimized:
            # AI optimization successful
            optimized_signal = ai_optimized
            optimization_type = "ai_enhanced"
        else:
            # Fallback to basic optimization
            optimized_signal = self._apply_basic_optimization(signal, technical_analysis)
            optimization_type = "basic"
            
        # Record optimization
        self._record_optimization(signal, optimized_signal, optimization_type)
        
        return optimized_signal
        
    def _apply_basic_optimization(self, signal, technical_analysis):
        """Apply basic optimization without AI"""
        optimized = signal.copy()
        pair = signal.get('pair', '')
        
        # Get technical analysis for this pair
        pair_analysis = technical_analysis.get(pair, {})
        
        # Adjust confidence based on technical factors
        base_confidence = signal.get('confidence', 0.5)
        adjustments = []
        
        # Trend alignment adjustment
        trend_direction = pair_analysis.get('primary_trend', 'neutral')
        signal_direction = signal.get('direction', '').lower()
        
        if trend_direction == 'bullish' and signal_direction == 'buy':
            adjustments.append(0.1)  # Boost for trend alignment
        elif trend_direction == 'bearish' and signal_direction == 'sell':
            adjustments.append(0.1)
        elif trend_direction != 'neutral' and (
            (trend_direction == 'bullish' and signal_direction == 'sell') or
            (trend_direction == 'bearish' and signal_direction == 'buy')
        ):
            adjustments.append(-0.15)  # Penalty for counter-trend
            
        # Volume confirmation
        volume_analysis = pair_analysis.get('volume_analysis', {})
        volume_trend = volume_analysis.get('volume_trend', 'neutral')
        
        if volume_trend == 'increasing':
            adjustments.append(0.05)
        elif volume_trend == 'decreasing':
            adjustments.append(-0.05)
            
        # Momentum confirmation
        momentum = pair_analysis.get('momentum', {})
        if isinstance(momentum, dict):
            momentum_score = momentum.get('momentum_score', 0.5)
            if momentum_score > 0.7:
                adjustments.append(0.05)
            elif momentum_score < 0.3:
                adjustments.append(-0.05)
                
        # Apply adjustments
        total_adjustment = sum(adjustments)
        optimized_confidence = base_confidence + total_adjustment
        
        # Clamp confidence between 0.1 and 0.95
        optimized_confidence = max(0.1, min(0.95, optimized_confidence))
        
        optimized['adjusted_confidence'] = optimized_confidence
        optimized['confidence_adjustment'] = total_adjustment
        optimized['optimization_type'] = 'basic'
        optimized['adjustment_reasons'] = adjustments
        
        return optimized
        
    def _record_optimization(self, original_signal, optimized_signal, optimization_type):
        """Record optimization details"""
        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'pair': original_signal.get('pair', ''),
            'original_confidence': original_signal.get('confidence', 0),
            'optimized_confidence': optimized_signal.get('adjusted_confidence', 0),
            'optimization_type': optimization_type,
            'confidence_change': optimized_signal.get('adjusted_confidence', 0) - original_signal.get('confidence', 0)
        }
        
        self.optimization_history.append(record)
        
        # Keep history manageable
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-1000:]
            
    async def calculate_optimization_effectiveness(self, lookback_days=7):
        """Calculate optimization effectiveness"""
        recent_optimizations = [
            opt for opt in self.optimization_history
            if self._is_recent(opt['timestamp'], lookback_days)
        ]
        
        if not recent_optimizations:
            return {
                'total_optimizations': 0,
                'average_confidence_boost': 0,
                'effectiveness_score': 0.5
            }
            
        # Calculate average confidence boost
        confidence_boosts = [opt['confidence_change'] for opt in recent_optimizations]
        avg_boost = sum(confidence_boosts) / len(confidence_boosts)
        
        # Calculate effectiveness (positive boosts are good)
        effectiveness = 0.5 + (avg_boost * 2)  # Convert to 0-1 scale
        
        return {
            'total_optimizations': len(recent_optimizations),
            'average_confidence_boost': avg_boost,
            'effectiveness_score': max(0, min(1, effectiveness))
        }
        
    def _is_recent(self, timestamp, max_days):
        """Check if timestamp is within max_days"""
        try:
            record_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_diff = (datetime.utcnow() - record_time).total_seconds()
            return time_diff <= (max_days * 24 * 3600)
        except:
            return False
            
    async def get_optimization_stats(self):
        """Get optimization statistics"""
        stats = {
            'total_optimizations': len(self.optimization_history),
            'recent_optimizations': len([opt for opt in self.optimization_history 
                                       if self._is_recent(opt['timestamp'], 1)]),
            'ai_optimizations': len([opt for opt in self.optimization_history 
                                   if opt.get('optimization_type') == 'ai_enhanced']),
            'basic_optimizations': len([opt for opt in self.optimization_history 
                                      if opt.get('optimization_type') == 'basic'])
        }
        
        if self.optimization_history:
            recent = [opt for opt in self.optimization_history 
                     if self._is_recent(opt['timestamp'], 7)]
            if recent:
                avg_boost = sum(opt['confidence_change'] for opt in recent) / len(recent)
                stats['avg_recent_boost'] = avg_boost
                
        return stats
        
    async def cleanup(self):
        """Cleanup optimizer"""
        self.optimization_history.clear()
        logging.info("🔒 DeepSeek optimizer cleanup completed")
