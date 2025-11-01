"""
DEEPSEEK REASONER - Analisa konteks harga mendalam
"""

import logging
import asyncio
from datetime import datetime
from config import settings

class DeepSeekReasoner:
    def __init__(self):
        self.connector = None
        self.reasoning_memory = []
        
    async def initialize(self, connector):
        """Initialize DeepSeek reasoner"""
        logging.info("🤔 INITIALIZING DEEPSEEK REASONER...")
        self.connector = connector
        
    async def analyze_price_context(self, market_data, technical_analysis, historical_patterns):
        """Analyze deep price context using AI reasoning"""
        if not self.connector or not self.connector.enabled:
            return self._fallback_analysis(technical_analysis)
            
        try:
            # Prepare comprehensive analysis data
            analysis_data = {
                'market_data': market_data,
                'technical_analysis': technical_analysis,
                'historical_patterns': historical_patterns,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Get AI analysis
            ai_analysis = await self.connector.analyze_market_context(
                market_data, 
                technical_analysis
            )
            
            if ai_analysis:
                # Enhance with reasoning
                enhanced_analysis = self._enhance_with_reasoning(ai_analysis, analysis_data)
                self._store_reasoning(enhanced_analysis)
                return enhanced_analysis
            else:
                return self._fallback_analysis(technical_analysis)
                
        except Exception as e:
            logging.error(f"❌ Price context analysis error: {e}")
            return self._fallback_analysis(technical_analysis)
            
    def _enhance_with_reasoning(self, ai_analysis, analysis_data):
        """Enhance AI analysis with additional reasoning"""
        enhanced = ai_analysis.copy()
        
        # Add reasoning metadata
        enhanced['reasoning_timestamp'] = datetime.utcnow().isoformat()
        enhanced['reasoning_engine'] = 'deepseek_v1'
        
        # Enhance probability analysis
        if 'probability_analysis' in enhanced:
            enhanced['probability_analysis'] = self._refine_probabilities(
                enhanced['probability_analysis'],
                analysis_data['technical_analysis']
            )
            
        # Enhance trading signals
        if 'trading_signals' in enhanced:
            enhanced['trading_signals'] = self._validate_signals(
                enhanced['trading_signals'],
                analysis_data['market_data']
            )
            
        # Add multi-timeframe confirmation
        enhanced['multi_tf_confirmation'] = self._check_multi_tf_confirmation(
            analysis_data['technical_analysis']
        )
        
        return enhanced
        
    def _refine_probabilities(self, probability_analysis, technical_analysis):
        """Refine probability analysis with technical confirmation"""
        refined = probability_analysis.copy()
        
        # Get technical confirmation strength
        tech_strength = self._calculate_technical_strength(technical_analysis)
        
        # Adjust probabilities based on technical strength
        if 'bullish_probability' in refined and 'bearish_probability' in refined:
            bull_prob = refined['bullish_probability']
            bear_prob = refined['bearish_probability']
            
            # Apply technical confirmation
            if tech_strength > 0.7:  # Strong technical confirmation
                adjustment = 0.1
            elif tech_strength > 0.5:  # Moderate confirmation
                adjustment = 0.05
            else:  # Weak confirmation
                adjustment = -0.05
                
            # Apply adjustment to dominant probability
            if bull_prob > bear_prob:
                refined['bullish_probability'] = min(bull_prob + adjustment, 0.95)
                refined['bearish_probability'] = max(bear_prob - adjustment, 0.05)
            else:
                refined['bullish_probability'] = max(bull_prob - adjustment, 0.05)
                refined['bearish_probability'] = min(bear_prob + adjustment, 0.95)
                
            # Update overall confidence
            refined['confidence'] = (refined.get('confidence', 0.5) + tech_strength) / 2
            
        return refined
        
    def _calculate_technical_strength(self, technical_analysis):
        """Calculate overall technical strength"""
        if not technical_analysis:
            return 0.5
            
        strengths = []
        
        for pair_analysis in technical_analysis.values():
            # Trend strength
            trend_strength = pair_analysis.get('trend_strength', 0.5)
            strengths.append(trend_strength)
            
            # Momentum strength
            momentum = pair_analysis.get('momentum', {})
            if isinstance(momentum, dict):
                momentum_score = momentum.get('momentum_score', 0.5)
                strengths.append(momentum_score)
                
        return sum(strengths) / len(strengths) if strengths else 0.5
        
    def _validate_signals(self, signals, market_data):
        """Validate AI signals with market data"""
        validated_signals = []
        
        for signal in signals:
            pair = signal.get('pair', '')
            direction = signal.get('direction', '')
            confidence = signal.get('confidence', 0.5)
            
            if pair in market_data:
                market_info = market_data[pair]
                
                # Validate with current market conditions
                validation_score = self._validate_signal_with_market(
                    signal, market_info
                )
                
                # Adjust confidence based on validation
                adjusted_confidence = confidence * validation_score
                
                validated_signal = signal.copy()
                validated_signal['adjusted_confidence'] = adjusted_confidence
                validated_signal['validation_score'] = validation_score
                validated_signals.append(validated_signal)
                
        return validated_signals
        
    def _validate_signal_with_market(self, signal, market_info):
        """Validate signal with current market info"""
        score = 1.0
        
        # Check if signal direction matches price momentum
        price_change = market_info.get('price_change_percent_24h', 0)
        direction = signal.get('direction', '')
        
        if direction == 'buy' and price_change < -5:
            score *= 0.7  # Reduce score for buying in strong downtrend
            
        elif direction == 'sell' and price_change > 5:
            score *= 0.7  # Reduce score for selling in strong uptrend
            
        # Check volume confirmation
        volume = market_info.get('volume_24h', 0)
        if volume == 0:
            score *= 0.8  # Reduce score for low volume
            
        return max(score, 0.3)  # Minimum 30% score
        
    def _check_multi_tf_confirmation(self, technical_analysis):
        """Check multi-timeframe confirmation"""
        confirmation = {
            'confirmed': False,
            'timeframes_aligned': 0,
            'primary_trend': 'neutral',
            'strength': 'weak'
        }
        
        if not technical_analysis:
            return confirmation
            
        # Count aligned timeframes for each pair
        for pair_analysis in technical_analysis.values():
            mtf_alignment = pair_analysis.get('multiple_timeframe_alignment', {})
            
            if mtf_alignment.get('aligned', False):
                confirmation['timeframes_aligned'] += 1
                confirmation['primary_trend'] = mtf_alignment.get('direction', 'neutral')
                
        # Determine confirmation strength
        total_pairs = len(technical_analysis)
        if total_pairs > 0:
            alignment_ratio = confirmation['timeframes_aligned'] / total_pairs
            
            if alignment_ratio >= 0.7:
                confirmation['confirmed'] = True
                confirmation['strength'] = 'strong'
            elif alignment_ratio >= 0.5:
                confirmation['confirmed'] = True
                confirmation['strength'] = 'medium'
            elif alignment_ratio >= 0.3:
                confirmation['strength'] = 'weak'
                
        return confirmation
        
    def _fallback_analysis(self, technical_analysis):
        """Fallback analysis when AI is unavailable"""
        return {
            'market_structure': 'neutral',
            'probability_analysis': {
                'bullish_probability': 0.5,
                'bearish_probability': 0.5,
                'confidence': 0.5
            },
            'trading_signals': [],
            'risk_assessment': 'medium',
            'reasoning': 'Fallback analysis - AI unavailable',
            'fallback_used': True
        }
        
    def _store_reasoning(self, analysis):
        """Store reasoning in memory"""
        reasoning_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis': analysis,
            'memory_id': f"reasoning_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        }
        
        self.reasoning_memory.append(reasoning_entry)
        
        # Keep only recent entries
        if len(self.reasoning_memory) > 100:
            self.reasoning_memory = self.reasoning_memory[-100:]
            
    async def get_context_for_pair(self, pair, lookback_hours=24):
        """Get historical context for specific pair"""
        relevant_reasoning = []
        
        for reasoning in self.reasoning_memory:
            # Check if reasoning is recent enough
            reasoning_time = datetime.fromisoformat(reasoning['timestamp'].replace('Z', '+00:00'))
            time_diff = (datetime.utcnow() - reasoning_time).total_seconds()
            
            if time_diff <= lookback_hours * 3600:
                # Check if this reasoning contains the pair
                analysis = reasoning['analysis']
                signals = analysis.get('trading_signals', [])
                
                for signal in signals:
                    if signal.get('pair') == pair:
                        relevant_reasoning.append(reasoning)
                        break
                        
        return relevant_reasoning
        
    async def cleanup(self):
        """Cleanup reasoner"""
        self.reasoning_memory.clear()
        logging.info("🔒 DeepSeek reasoner cleanup completed")
