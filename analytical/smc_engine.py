"""
SMART MONEY CONCEPT ENGINE - Logic Smart Money Concept
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class SMCEngine:
    def __init__(self):
        self.setup_smc_models()
        
    def setup_smc_models(self):
        """Setup model SMC"""
        self.liquidity_levels = {}
        self.order_blocks = {}
        self.breakeven_points = {}
        
    async def initialize(self):
        """Initialize SMC engine"""
        logging.info("💎 INITIALIZING SMART MONEY CONCEPT ENGINE...")
        
    async def analyze(self, market_data, structure_analysis):
        """Analisis berdasarkan Smart Money Concept"""
        smc_analysis = {}
        
        for pair, data in market_data.items():
            try:
                analysis = await self._analyze_pair_smc(pair, data, structure_analysis.get(pair, {}))
                smc_analysis[pair] = analysis
            except Exception as e:
                logging.error(f"❌ SMC analysis error for {pair}: {e}")
                continue
                
        return smc_analysis
        
    async def _analyze_pair_smc(self, pair, data, structure_data):
        """Analisis SMC untuk satu pair"""
        analysis = {
            'liquidity_pools': [],
            'order_blocks': [],
            'mitigation_blocks': [],
            'breakeven_points': [],
            'fair_value_gaps': [],
            'market_structure': {},
            'manipulation_zones': [],
            'smart_money_signal': 'neutral'
        }
        
        if len(data) < 50:
            return analysis
            
        df = pd.DataFrame(data)
        
        # 1. Identifikasi Liquidity Pools
        analysis['liquidity_pools'] = self._find_liquidity_pools(df)
        
        # 2. Identifikasi Order Blocks
        analysis['order_blocks'] = self._find_order_blocks(df)
        
        # 3. Mitigation Blocks
        analysis['mitigation_blocks'] = self._find_mitigation_blocks(df)
        
        # 4. Breakeven Points
        analysis['breakeven_points'] = self._find_breakeven_points(df)
        
        # 5. Fair Value Gaps
        analysis['fair_value_gaps'] = self._find_fair_value_gaps(df)
        
        # 6. Market Structure Analysis
        analysis['market_structure'] = self._analyze_market_structure(df)
        
        # 7. Manipulation Zones
        analysis['manipulation_zones'] = self._find_manipulation_zones(df)
        
        # 8. Smart Money Signal
        analysis['smart_money_signal'] = self._generate_smc_signal(analysis)
        
        return analysis
        
    def _find_liquidity_pools(self, df):
        """Temukan liquidity pools (significant highs/lows)"""
        pools = []
        
        # Significant highs (liquidity above)
        highs = df['high'].values
        for i in range(2, len(highs)-2):
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                pools.append({
                    'price': highs[i],
                    'type': 'liquidity_above',
                    'strength': 'strong',
                    'timestamp': df.iloc[i]['timestamp']
                })
                
        # Significant lows (liquidity below)
        lows = df['low'].values
        for i in range(2, len(lows)-2):
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                pools.append({
                    'price': lows[i],
                    'type': 'liquidity_below', 
                    'strength': 'strong',
                    'timestamp': df.iloc[i]['timestamp']
                })
                
        return pools
        
    def _find_order_blocks(self, df):
        """Temukan order blocks (significant candle bodies)"""
        blocks = []
        
        for i in range(1, len(df)-1):
            candle = df.iloc[i]
            body_size = abs(candle['close'] - candle['open'])
            total_range = candle['high'] - candle['low']
            body_ratio = body_size / total_range if total_range > 0 else 0
            
            # Order block criteria: large body candle followed by price movement
            if body_ratio > 0.7:
                next_candle = df.iloc[i+1]
                
                # Bullish OB: large bear candle followed by bullish movement
                if (candle['close'] < candle['open'] and 
                    next_candle['close'] > candle['high']):
                    blocks.append({
                        'price_range': [candle['low'], candle['high']],
                        'type': 'bullish_ob',
                        'strength': 'strong',
                        'timestamp': candle['timestamp']
                    })
                    
                # Bearish OB: large bull candle followed by bearish movement  
                elif (candle['close'] > candle['open'] and
                      next_candle['close'] < candle['low']):
                    blocks.append({
                        'price_range': [candle['low'], candle['high']],
                        'type': 'bearish_ob',
                        'strength': 'strong', 
                        'timestamp': candle['timestamp']
                    })
                    
        return blocks
        
    def _find_mitigation_blocks(self, df):
        """Temukan mitigation blocks (areas where price returns to fill)"""
        blocks = []
        
        for i in range(5, len(df)-1):
            current = df.iloc[i]
            prev_high = max(df.iloc[i-5:i]['high'])
            prev_low = min(df.iloc[i-5:i]['low'])
            
            # Price returning to previous high/low (mitigation)
            if (abs(current['close'] - prev_high) / prev_high < 0.002 or
                abs(current['close'] - prev_low) / prev_low < 0.002):
                blocks.append({
                    'price': current['close'],
                    'type': 'mitigation_block',
                    'previous_level': prev_high if abs(current['close'] - prev_high) < abs(current['close'] - prev_low) else prev_low,
                    'timestamp': current['timestamp']
                })
                
        return blocks
        
    def _find_breakeven_points(self, df):
        """Temukan breakeven points (areas where positions might break even)"""
        points = []
        
        # Simplified: areas where price consolidated previously
        for i in range(10, len(df)-5):
            window = df.iloc[i-5:i]
            volatility = (window['high'].max() - window['low'].min()) / window['close'].mean()
            
            if volatility < 0.01:  # Low volatility consolidation
                points.append({
                    'price_range': [window['low'].min(), window['high'].max()],
                    'type': 'breakeven_zone',
                    'timestamp': df.iloc[i]['timestamp']
                })
                
        return points
        
    def _find_fair_value_gaps(self, df):
        """Temukan Fair Value Gaps"""
        fvgs = []
        
        for i in range(1, len(df)-1):
            current = df.iloc[i]
            previous = df.iloc[i-1]
            
            # Bullish FVG
            if current['low'] > previous['high']:
                fvgs.append({
                    'price_range': [previous['high'], current['low']],
                    'type': 'bullish_fvg',
                    'strength': 'medium',
                    'timestamp': current['timestamp']
                })
                
            # Bearish FVG
            elif current['high'] < previous['low']:
                fvgs.append({
                    'price_range': [current['high'], previous['low']],
                    'type': 'bearish_fvg', 
                    'strength': 'medium',
                    'timestamp': current['timestamp']
                })
                
        return fvgs
        
    def _analyze_market_structure(self, df):
        """Analisis struktur pasar SMC"""
        structure = {
            'bos_count': 0,
            'choch_count': 0,
            'liquidity_takes': 0,
            'manipulation_signs': 0
        }
        
        highs = df['high'].values
        lows = df['low'].values
        
        # Count BOS and CHoCH
        for i in range(3, len(highs)-1):
            # Break of Structure
            if highs[i] > max(highs[i-3:i]):
                structure['bos_count'] += 1
                
            # Change of Character
            if (highs[i] < highs[i-1] and highs[i-1] > highs[i-2] and
                lows[i] < lows[i-1] and lows[i-1] > lows[i-2]):
                structure['choch_count'] += 1
                
        return structure
        
    def _find_manipulation_zones(self, df):
        """Temukan zona manipulasi (stop hunts)"""
        zones = []
        
        for i in range(3, len(df)-1):
            current = df.iloc[i]
            prev = df.iloc[i-1]
            
            # Stop hunt pattern: wick beyond previous level then reversal
            if (current['low'] < prev['low'] and 
                current['close'] > prev['high'] and
                abs(current['close'] - current['open']) / (current['high'] - current['low']) > 0.6):
                zones.append({
                    'price': current['low'],
                    'type': 'bullish_stop_hunt',
                    'timestamp': current['timestamp']
                })
                
            elif (current['high'] > prev['high'] and
                  current['close'] < prev['low'] and
                  abs(current['close'] - current['open']) / (current['high'] - current['low']) > 0.6):
                zones.append({
                    'price': current['high'],
                    'type': 'bearish_stop_hunt', 
                    'timestamp': current['timestamp']
                })
                
        return zones
        
    def _generate_smc_signal(self, analysis):
        """Generate sinyal berdasarkan analisis SMC"""
        bullish_signals = 0
        bearish_signals = 0
        
        # Analisis bullish OB
        bullish_obs = [ob for ob in analysis['order_blocks'] if ob['type'] == 'bullish_ob']
        if bullish_obs and analysis.get('market_structure', {}).get('bos_count', 0) > 0:
            bullish_signals += 1
            
        # Analisis bearish OB  
        bearish_obs = [ob for ob in analysis['order_blocks'] if ob['type'] == 'bearish_ob']
        if bearish_obs and analysis.get('market_structure', {}).get('choch_count', 0) > 0:
            bearish_signals += 1
            
        # Liquidity analysis
        liquidity_above = [lp for lp in analysis['liquidity_pools'] if lp['type'] == 'liquidity_above']
        liquidity_below = [lp for lp in analysis['liquidity_pools'] if lp['type'] == 'liquidity_below']
        
        if liquidity_above and not liquidity_below:
            bearish_signals += 1  # Price might move down to take liquidity
        elif liquidity_below and not liquidity_above:
            bullish_signals += 1  # Price might move up to take liquidity
            
        if bullish_signals > bearish_signals:
            return "bullish"
        elif bearish_signals > bullish_signals:
            return "bearish"
        else:
            return "neutral"
