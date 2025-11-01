"""
PATTERN RECOGNITION - Deteksi OB, FVG, SFP, MSS
"""

import logging
import numpy as np
from datetime import datetime

class PatternRecognition:
    def __init__(self):
        self.setup_patterns()
        
    def setup_patterns(self):
        """Setup pola yang akan diidentifikasi"""
        self.patterns = {
            'OB': self._detect_order_blocks,
            'FVG': self._detect_fvg,
            'SFP': self._detect_sfp,
            'MSS': self._detect_mss
        }
        
    async def initialize(self):
        """Initialize pattern recognition"""
        logging.info("🔍 INITIALIZING PATTERN RECOGNITION...")
        
    async def scan(self, tf_data):
        """Scan semua pairs dan timeframes untuk pola"""
        pattern_analysis = {}
        
        for pair, timeframes in tf_data.items():
            try:
                patterns = await self._scan_pair(pair, timeframes)
                pattern_analysis[pair] = patterns
            except Exception as e:
                logging.error(f"❌ Pattern scan error for {pair}: {e}")
                continue
                
        return pattern_analysis
        
    async def _scan_pair(self, pair, timeframes):
        """Scan pola untuk satu pair"""
        all_patterns = []
        
        for tf, data in timeframes.items():
            if len(data) < 10:
                continue
                
            tf_patterns = await self._scan_timeframe(data, tf)
            all_patterns.extend(tf_patterns)
            
        return {
            'patterns': all_patterns,
            'pattern_count': len(all_patterns),
            'strong_patterns': [p for p in all_patterns if p['strength'] == 'strong']
        }
        
    async def _scan_timeframe(self, data, timeframe):
        """Scan pola dalam satu timeframe"""
        patterns = []
        
        # Deteksi semua jenis pola
        for pattern_name, detector in self.patterns.items():
            detected = detector(data, timeframe)
            patterns.extend(detected)
            
        return patterns
        
    def _detect_order_blocks(self, data, timeframe):
        """Deteksi Order Blocks"""
        blocks = []
        
        # Simplified OB detection
        for i in range(2, len(data)-2):
            current = data[i]
            prev = data[i-1]
            next_candle = data[i+1]
            
            # Logic deteksi OB sederhana
            if (abs(current['open'] - current['close']) / (current['high'] - current['low']) > 0.7 and
                next_candle['close'] > current['high']):
                
                blocks.append({
                    'type': 'OB',
                    'price': current['close'],
                    'timeframe': timeframe,
                    'strength': 'strong',
                    'timestamp': datetime.utcnow(),
                    'direction': 'bullish'
                })
                
        return blocks
        
    def _detect_fvg(self, data, timeframe):
        """Deteksi Fair Value Gaps"""
        fvgs = []
        
        for i in range(1, len(data)-1):
            current = data[i]
            prev = data[i-1]
            
            # Logic FVG sederhana
            if (current['low'] > prev['high'] or  # Bullish FVG
                current['high'] < prev['low']):   # Bearish FVG
                
                fvgs.append({
                    'type': 'FVG',
                    'price_range': [min(current['low'], prev['low']), 
                                   max(current['high'], prev['high'])],
                    'timeframe': timeframe,
                    'strength': 'medium',
                    'timestamp': datetime.utcnow(),
                    'direction': 'bullish' if current['low'] > prev['high'] else 'bearish',
                    'active': True
                })
                
        return fvgs
        
    def _detect_sfp(self, data, timeframe):
        """Deteksi Stop Hunting Patterns"""
        sfps = []
        
        # Simplified SFP detection
        for i in range(3, len(data)):
            if (data[i]['low'] < data[i-1]['low'] and  # New low
                data[i]['close'] > data[i-1]['high']): # Strong close above previous high
                
                sfps.append({
                    'type': 'SFP',
                    'price': data[i]['low'],
                    'timeframe': timeframe,
                    'strength': 'strong',
                    'timestamp': datetime.utcnow(),
                    'direction': 'bullish'  # Bullish stop hunt
                })
                
        return sfps
        
    def _detect_mss(self, data, timeframe):
        """Deteksi Market Structure Shifts"""
        mss_patterns = []
        
        # Simplified MSS detection
        for i in range(5, len(data)-1):
            # Check for structure break
            if (data[i]['high'] > max([d['high'] for d in data[i-5:i]]) and
                data[i+1]['high'] < data[i]['high']):
                
                mss_patterns.append({
                    'type': 'MSS',
                    'price': data[i]['high'],
                    'timeframe': timeframe,
                    'strength': 'strong',
                    'timestamp': datetime.utcnow(),
                    'direction': 'bearish',
                    'confirmed': True
                })
                
        return mss_patterns
