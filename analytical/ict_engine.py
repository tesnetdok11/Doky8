"""
ICT ENGINE - ICT Fair Value Gap & Order Block Analysis
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ICTEngine:
    def __init__(self):
        self.setup_ict_concepts()
        
    def setup_ict_concepts(self):
        """Setup konsep ICT"""
        self.premium_ranges = {}
        self.discount_ranges = {}
        self.killer_zones = {}
        
    async def initialize(self):
        """Initialize ICT engine"""
        logging.info("🎯 INITIALIZING ICT ENGINE...")
        
    async def analyze(self, market_data, structure_analysis):
        """Analisis berdasarkan ICT concepts"""
        ict_analysis = {}
        
        for pair, data in market_data.items():
            try:
                analysis = await self._analyze_pair_ict(pair, data, structure_analysis.get(pair, {}))
                ict_analysis[pair] = analysis
            except Exception as e:
                logging.error(f"❌ ICT analysis error for {pair}: {e}")
                continue
                
        return ict_analysis
        
    async def _analyze_pair_ict(self, pair, data, structure_data):
        """Analisis ICT untuk satu pair"""
        analysis = {
            'fair_value_gaps': [],
            'order_blocks': [],
            'mitigation_blocks': [],
            'premium_discount_zones': [],
            'kill_zones': {},
            'market_structure_shift': False,
            'liquidity_voids': [],
            'optimal_trade_entry': None
        }
        
        if len(data) < 100:
            return analysis
            
        df = pd.DataFrame(data)
        
        # 1. Fair Value Gaps dengan filter ICT
        analysis['fair_value_gaps'] = self._find_ict_fvg(df)
        
        # 2. Order Blocks ICT
        analysis['order_blocks'] = self._find_ict_order_blocks(df)
        
        # 3. Mitigation Blocks
        analysis['mitigation_blocks'] = self._find_ict_mitigation_blocks(df)
        
        # 4. Premium/Discount Zones
        analysis['premium_discount_zones'] = self._find_premium_discount_zones(df)
        
        # 5. Kill Zones (Sesi pasar)
        analysis['kill_zones'] = self._analyze_kill_zones(df)
        
        # 6. Market Structure Shift
        analysis['market_structure_shift'] = self._detect_mss(df)
        
        # 7. Liquidity Voids
        analysis['liquidity_voids'] = self._find_liquidity_voids(df)
        
        # 8. Optimal Trade Entry
        analysis['optimal_trade_entry'] = self._find_optimal_entry(analysis)
        
        return analysis
        
    def _find_ict_fvg(self, df):
        """Temukan Fair Value Gaps dengan kriteria ICT"""
        fvgs = []
        
        for i in range(2, len(df)-1):
            current = df.iloc[i]
            previous = df.iloc[i-1]
            next_candle = df.iloc[i+1] if i < len(df)-1 else current
            
            # Bullish FVG: current low > previous high
            if current['low'] > previous['high']:
                # ICT Filter: next candle should not fill the gap completely
                if next_candle['low'] > previous['high']:
                    fvgs.append({
                        'price_range': [previous['high'], current['low']],
                        'type': 'bullish_fvg',
                        'strength': 'strong',
                        'timestamp': current['timestamp'],
                        'filled': False
                    })
                    
            # Bearish FVG: current high < previous low  
            elif current['high'] < previous['low']:
                if next_candle['high'] < previous['low']:
                    fvgs.append({
                        'price_range': [current['high'], previous['low']],
                        'type': 'bearish_fvg',
                        'strength': 'strong',
                        'timestamp': current['timestamp'],
                        'filled': False
                    })
                    
        return fvgs
        
    def _find_ict_order_blocks(self, df):
        """Temukan Order Blocks dengan kriteria ICT"""
        blocks = []
        
        for i in range(3, len(df)-2):
            candle = df.iloc[i]
            prev_candle = df.iloc[i-1]
            next_candle = df.iloc[i+1]
            
            body_size = abs(candle['close'] - candle['open'])
            total_range = candle['high'] - candle['low']
            body_ratio = body_size / total_range if total_range > 0 else 0
            
            # ICT OB: Strong candle dengan rejection
            if body_ratio > 0.8:
                # Bullish OB: Bear candle followed by strong bullish move
                if (candle['close'] < candle['open'] and
                    next_candle['close'] > candle['high'] and
                    abs(next_candle['close'] - next_candle['open']) / (next_candle['high'] - next_candle['low']) > 0.6):
                    
                    blocks.append({
                        'price_range': [candle['low'], candle['high']],
                        'type': 'bullish_ob',
                        'strength': 'strong',
                        'timestamp': candle['timestamp'],
                        'mitigated': False
                    })
                    
                # Bearish OB: Bull candle followed by strong bearish move
                elif (candle['close'] > candle['open'] and
                      next_candle['close'] < candle['low'] and
                      abs(next_candle['close'] - next_candle['open']) / (next_candle['high'] - next_candle['low']) > 0.6):
                    
                    blocks.append({
                        'price_range': [candle['low'], candle['high']],
                        'type': 'bearish_ob',
                        'strength': 'strong',
                        'timestamp': candle['timestamp'],
                        'mitigated': False
                    })
                    
        return blocks
        
    def _find_ict_mitigation_blocks(self, df):
        """Temukan mitigation blocks (areas where price returns to fill FVG/OB)"""
        blocks = []
        
        # Check for FVG mitigation
        fvgs = self._find_ict_fvg(df)
        for fvg in fvgs:
            fvg_low = min(fvg['price_range'])
            fvg_high = max(fvg['price_range'])
            
            # Check if price returned to fill the FVG
            for i in range(len(df)):
                if (df.iloc[i]['low'] <= fvg_high and 
                    df.iloc[i]['high'] >= fvg_low):
                    blocks.append({
                        'price_range': fvg['price_range'],
                        'type': 'fvg_mitigation',
                        'original_type': fvg['type'],
                        'timestamp': df.iloc[i]['timestamp']
                    })
                    break
                    
        return blocks
        
    def _find_premium_discount_zones(self, df):
        """Temukan zona premium/discount berdasarkan recent range"""
        zones = []
        
        if len(df) < 20:
            return zones
            
        recent_high = df['high'].iloc[-20:].max()
        recent_low = df['low'].iloc[-20:].min()
        recent_range = recent_high - recent_low
        
        # Premium zone (upper 1/3)
        premium_low = recent_high - (recent_range / 3)
        zones.append({
            'price_range': [premium_low, recent_high],
            'type': 'premium_zone',
            'strength': 'medium'
        })
        
        # Discount zone (lower 1/3)
        discount_high = recent_low + (recent_range / 3)
        zones.append({
            'price_range': [recent_low, discount_high],
            'type': 'discount_zone',
            'strength': 'medium'
        })
        
        return zones
        
    def _analyze_kill_zones(self, df):
        """Analisis kill zones berdasarkan waktu pasar"""
        kill_zones = {
            'london_open': False,
            'newyork_open': False,
            'asian_session': False
        }
        
        # Simplified time-based analysis
        current_hour = datetime.utcnow().hour
        
        # London Kill Zone: 7:00 - 10:00 UTC
        if 7 <= current_hour < 10:
            kill_zones['london_open'] = True
            
        # New York Kill Zone: 13:00 - 16:00 UTC
        if 13 <= current_hour < 16:
            kill_zones['newyork_open'] = True
            
        # Asian Session: 00:00 - 08:00 UTC
        if 0 <= current_hour < 8:
            kill_zones['asian_session'] = True
            
        return kill_zones
        
    def _detect_mss(self, df):
        """Deteksi Market Structure Shift"""
        if len(df) < 20:
            return False
            
        highs = df['high'].values
        lows = df['low'].values
        
        # Check for recent structure break
        recent_high = max(highs[-5:])
        previous_high = max(highs[-10:-5])
        
        recent_low = min(lows[-5:])
        previous_low = min(lows[-10:-5])
        
        # MSS: Break of previous high/low with confirmation
        if (recent_high > previous_high and 
            df['close'].iloc[-1] > previous_high):
            return True
            
        if (recent_low < previous_low and
            df['close'].iloc[-1] < previous_low):
            return True
            
        return False
        
    def _find_liquidity_voids(self, df):
        """Temukan liquidity voids (areas dengan sedikit trading)"""
        voids = []
        
        # Areas with low volume and small ranges
        for i in range(10, len(df)-5):
            window = df.iloc[i-5:i]
            avg_volume = window['volume'].mean()
            avg_range = (window['high'] - window['low']).mean()
            price_level = window['close'].mean()
            
            if (avg_volume < df['volume'].mean() * 0.5 and
                avg_range < (df['high'] - df['low']).mean() * 0.5):
                voids.append({
                    'price': price_level,
                    'type': 'liquidity_void',
                    'timestamp': df.iloc[i]['timestamp']
                })
                
        return voids
        
    def _find_optimal_entry(self, analysis):
        """Temukan optimal trade entry berdasarkan analisis ICT"""
        entries = []
        
        # Combine FVG and OB for entry signals
        for fvg in analysis['fair_value_gaps']:
            if not fvg['filled']:
                entries.append({
                    'type': 'fvg_entry',
                    'price_range': fvg['price_range'],
                    'direction': 'bullish' if fvg['type'] == 'bullish_fvg' else 'bearish',
                    'confidence': 'high'
                })
                
        for ob in analysis['order_blocks']:
            if not ob['mitigated']:
                entries.append({
                    'type': 'ob_entry',
                    'price_range': ob['price_range'],
                    'direction': 'bullish' if ob['type'] == 'bullish_ob' else 'bearish',
                    'confidence': 'high'
                })
                
        # Return the highest confidence entry
        if entries:
            return max(entries, key=lambda x: 1 if x['confidence'] == 'high' else 0)
            
        return None
