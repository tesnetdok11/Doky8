"""
PROBABILITY ENGINE - Menghitung confidence level sinyal
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from config import settings

class ProbabilityEngine:
    def __init__(self):
        self.setup_probability_models()
        
    def setup_probability_models(self):
        """Setup model probabilitas"""
        self.models = {
            'structure_based': self._structure_probability,
            'pattern_based': self._pattern_probability,
            'volume_based': self._volume_probability,
            'momentum_based': self._momentum_probability
        }
        
        self.weights = {
            'structure_based': 0.35,
            'pattern_based': 0.30, 
            'volume_based': 0.20,
            'momentum_based': 0.15
        }
        
    async def initialize(self):
        """Initialize probability engine"""
        logging.info("🎲 INITIALIZING PROBABILITY ENGINE...")
        
    async def calculate(self, structure_analysis, pattern_analysis):
        """Hitung probabilitas keseluruhan"""
        probabilities = {}
        
        for pair in structure_analysis.keys():
            try:
                # Hitung probabilitas per komponen
                struct_prob = self._structure_probability(structure_analysis[pair])
                pattern_prob = self._pattern_probability(pattern_analysis.get(pair, {}))
                volume_prob = self._volume_probability(structure_analysis[pair])
                momentum_prob = self._momentum_probability(structure_analysis[pair])
                
                # Weighted average
                total_prob = (
                    struct_prob * self.weights['structure_based'] +
                    pattern_prob * self.weights['pattern_based'] +
                    volume_prob * self.weights['volume_based'] +
                    momentum_prob * self.weights['momentum_based']
                )
                
                # Probabilitas BUY vs SELL
                buy_prob, sell_prob = self._directional_probability(
                    structure_analysis[pair], pattern_analysis.get(pair, {})
                )
                
                probabilities[pair] = {
                    'confidence': total_prob,
                    'buy_probability': buy_prob,
                    'sell_probability': sell_prob,
                    'reason': self._generate_reason(
                        struct_prob, pattern_prob, volume_prob, momentum_prob
                    )
                }
                
            except Exception as e:
                logging.error(f"❌ Probability calculation error for {pair}: {e}")
                continue
                
        return probabilities
        
    def _structure_probability(self, structure_data):
        """Hitung probabilitas berdasarkan struktur pasar"""
        score = 0.0
        factors = 0
        
        if structure_data.get('trend_strength', 0) > 0.7:
            score += 0.8
            factors += 1
            
        if structure_data.get('liquidity_zones', []):
            score += 0.7
            factors += 1
            
        if structure_data.get('bos_confirmed', False):
            score += 0.9
            factors += 1
            
        if structure_data.get('choch_confirmed', False):
            score += 0.8
            factors += 1
            
        return score / factors if factors > 0 else 0.5
        
    def _pattern_probability(self, pattern_data):
        """Hitung probabilitas berdasarkan pola"""
        if not pattern_data:
            return 0.5
            
        score = 0.0
        patterns = pattern_data.get('patterns', [])
        
        for pattern in patterns:
            if pattern['type'] == 'OB' and pattern['strength'] == 'strong':
                score += 0.8
            elif pattern['type'] == 'FVG' and pattern['active']:
                score += 0.7
            elif pattern['type'] == 'MSS' and pattern['confirmed']:
                score += 0.75
                
        return min(score / max(len(patterns), 1), 1.0)
        
    def _volume_probability(self, structure_data):
        """Hitung probabilitas berdasarkan volume"""
        volume_data = structure_data.get('volume_analysis', {})
        if not volume_data:
            return 0.5
            
        score = 0.0
        factors = 0
        
        if volume_data.get('volume_trend', '') == 'increasing':
            score += 0.7
            factors += 1
            
        if volume_data.get('delta_positive', False):
            score += 0.6
            factors += 1
            
        if volume_data.get('oi_increasing', False):
            score += 0.5
            factors += 1
            
        return score / factors if factors > 0 else 0.5
        
    def _momentum_probability(self, structure_data):
        """Hitung probabilitas berdasarkan momentum"""
        momentum_data = structure_data.get('momentum', {})
        if not momentum_data:
            return 0.5
            
        rsi = momentum_data.get('rsi', 50)
        if 30 < rsi < 70:  # Tidak overbought/oversold
            score = 0.7
        else:
            score = 0.4
            
        return score
        
    def _directional_probability(self, structure_data, pattern_data):
        """Tentukan probabilitas arah"""
        trend_direction = structure_data.get('trend_direction', 'neutral')
        
        if trend_direction == 'bullish':
            return 0.7, 0.3
        elif trend_direction == 'bearish':
            return 0.3, 0.7
        else:
            return 0.5, 0.5
            
    def _generate_reason(self, struct_prob, pattern_prob, volume_prob, momentum_prob):
        """Generate alasan untuk probabilitas"""
        reasons = []
        
        if struct_prob > 0.7:
            reasons.append("Strong market structure")
        if pattern_prob > 0.7:
            reasons.append("High pattern confidence") 
        if volume_prob > 0.6:
            reasons.append("Supportive volume")
        if momentum_prob > 0.6:
            reasons.append("Good momentum")
            
        return ", ".join(reasons) if reasons else "Mixed signals"
