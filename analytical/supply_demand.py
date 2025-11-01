"""
SUPPLY DEMAND ENGINE - Pemetaan zona Supply & Demand
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SupplyDemandEngine:
    def __init__(self):
        self.setup_sd_zones()
        
    def setup_sd_zones(self):
        """Setup zona supply demand"""
        self.supply_zones = {}
        self.demand_zones = {}
        self.zone_strength_threshold = 0.7
        
    async def initialize(self):
        """Initialize supply demand engine"""
        logging.info("⚖️ INITIALIZING SUPPLY DEMAND ENGINE...")
        
    async def analyze(self, market_data, structure_analysis):
        """Analisis zona supply demand"""
        sd_analysis = {}
        
        for pair, data in market_data.items():
            try:
                analysis = await self._analyze_pair_sd(pair, data, structure_analysis.get(pair, {}))
                sd_analysis[pair] = analysis
            except Exception as e:
                logging.error(f"❌ Supply demand analysis error for {pair}: {e}")
                continue
                
        return sd_analysis
        
    async def _analyze_pair_sd(self, pair, data, structure_data):
        """Analisis supply demand untuk satu pair"""
        analysis = {
            'supply_zones': [],
            'demand_zones': [],
            'zone_strength': 'neutral',
            'imbalance_zones': [],
            'fresh_zones': [],
            'tested_zones': [],
            'zone_quality_score': 0.0
        }
        
        if len(data) < 100:
            return analysis
            
        df = pd.DataFrame(data)
        
        # 1. Identifikasi Supply Zones
        analysis['supply_zones'] = self._find_supply_zones(df)
        
        # 2. Identifikasi Demand Zones  
        analysis['demand_zones'] = self._find_demand_zones(df)
        
        # 3. Analisis Strength Zones
        analysis['zone_strength'] = self._analyze_zone_strength(analysis)
        
        # 4. Imbalance Zones
        analysis['imbalance_zones'] = self._find_imbalance_zones(df)
        
        # 5. Fresh vs Tested Zones
        analysis['fresh_zones'] = self._find_fresh_zones(analysis, df)
        analysis['tested_zones'] = self._find_tested_zones(analysis, df)
        
        # 6. Zone Quality Score
        analysis['zone_quality_score'] = self._calculate_zone_quality(analysis)
        
        return analysis
        
    def _find_supply_zones(self, df):
        """Temukan zona supply (resistance)"""
        supply_zones = []
        
        # Find significant swing highs
        for i in range(5, len(df)-5):
            if self._is_swing_high(df, i):
                zone = self._create_supply_zone(df, i)
                if zone and self._is_valid_zone(zone, supply_zones):
                    supply_zones.append(zone)
                    
        return supply_zones
        
    def _find_demand_zones(self, df):
        """Temukan zona demand (support)"""
        demand_zones = []
        
        # Find significant swing lows
        for i in range(5, len(df)-5):
            if self._is_swing_low(df, i):
                zone = self._create_demand_zone(df, i)
                if zone and self._is_valid_zone(zone, demand_zones):
                    demand_zones.append(zone)
                    
        return demand_zones
        
    def _is_swing_high(self, df, index):
        """Cek apakah titik adalah swing high"""
        if index < 5 or index > len(df) - 5:
            return False
            
        current_high = df.iloc[index]['high']
        
        # Check left side (lower highs)
        left_highs = [df.iloc[i]['high'] for i in range(index-5, index)]
        if any(h > current_high for h in left_highs):
            return False
            
        # Check right side (lower highs)  
        right_highs = [df.iloc[i]['high'] for i in range(index+1, index+6)]
        if any(h > current_high for h in right_highs):
            return False
            
        return True
        
    def _is_swing_low(self, df, index):
        """Cek apakah titik adalah swing low"""
        if index < 5 or index > len(df) - 5:
            return False
            
        current_low = df.iloc[index]['low']
        
        # Check left side (higher lows)
        left_lows = [df.iloc[i]['low'] for i in range(index-5, index)]
        if any(l < current_low for l in left_lows):
            return False
            
        # Check right side (higher lows)
        right_lows = [df.iloc[i]['low'] for i in range(index+1, index+6)]
        if any(l < current_low for l in right_lows):
            return False
            
        return True
        
    def _create_supply_zone(self, df, index):
        """Buat zona supply dari swing high"""
        candle = df.iloc[index]
        base_price = candle['low']
        zone_height = (candle['high'] - candle['low']) * 1.5  # Extended zone
        
        return {
            'price_range': [base_price, base_price + zone_height],
            'strength': 'strong',
            'origin_timestamp': candle['timestamp'],
            'type': 'supply',
            'test_count': 0,
            'last_test': None,
            'base_candle': {
                'open': candle['open'],
                'high': candle['high'], 
                'low': candle['low'],
                'close': candle['close']
            }
        }
        
    def _create_demand_zone(self, df, index):
        """Buat zona demand dari swing low"""
        candle = df.iloc[index]
        base_price = candle['high']
        zone_height = (candle['high'] - candle['low']) * 1.5  # Extended zone
        
        return {
            'price_range': [base_price - zone_height, base_price],
            'strength': 'strong',
            'origin_timestamp': candle['timestamp'],
            'type': 'demand', 
            'test_count': 0,
            'last_test': None,
            'base_candle': {
                'open': candle['open'],
                'high': candle['high'],
                'low': candle['low'], 
                'close': candle['close']
            }
        }
        
    def _is_valid_zone(self, new_zone, existing_zones):
        """Cek apakah zona valid (tidak overlap signifikan)"""
        new_low = min(new_zone['price_range'])
        new_high = max(new_zone['price_range'])
        
        for existing_zone in existing_zones:
            exist_low = min(existing_zone['price_range'])
            exist_high = max(existing_zone['price_range'])
            
            # Check for significant overlap
            overlap_ratio = (min(new_high, exist_high) - max(new_low, exist_low)) / (new_high - new_low)
            if overlap_ratio > 0.3:  # 30% overlap threshold
                return False
                
        return True
        
    def _analyze_zone_strength(self, analysis):
        """Analisis strength zona"""
        supply_count = len(analysis['supply_zones'])
        demand_count = len(analysis['demand_zones'])
        
        if supply_count > demand_count * 1.5:
            return "supply_dominant"
        elif demand_count > supply_count * 1.5:
            return "demand_dominant"
        else:
            return "balanced"
            
    def _find_imbalance_zones(self, df):
        """Temukan zona imbalance (large moves)"""
        imbalances = []
        
        for i in range(1, len(df)-1):
            current = df.iloc[i]
            previous = df.iloc[i-1]
            
            # Price gap atau large move
            price_gap = abs(current['open'] - previous['close']) / previous['close']
            if price_gap > 0.005:  # 0.5% gap
                imbalances.append({
                    'price_range': [min(current['open'], previous['close']), 
                                   max(current['open'], previous['close'])],
                    'type': 'price_gap',
                    'timestamp': current['timestamp']
                })
                
        return imbalances
        
    def _find_fresh_zones(self, analysis, df):
        """Temukan zona fresh (belum di-test)"""
        fresh_zones = []
        current_price = df.iloc[-1]['close']
        
        for zone in analysis['supply_zones'] + analysis['demand_zones']:
            zone_low = min(zone['price_range'])
            zone_high = max(zone['price_range'])
            
            # Zone is fresh if price hasn't revisited since creation
            zone_time = zone['origin_timestamp']
            zone_index = df[df['timestamp'] == zone_time].index[0] if zone_time in df['timestamp'].values else -1
            
            if zone_index != -1:
                # Check if price returned to zone after creation
                subsequent_data = df.iloc[zone_index+1:]
                zone_tests = subsequent_data[
                    (subsequent_data['low'] <= zone_high) & 
                    (subsequent_data['high'] >= zone_low)
                ]
                
                if len(zone_tests) == 0:
                    fresh_zones.append(zone)
                    
        return fresh_zones
        
    def _find_tested_zones(self, analysis, df):
        """Temukan zona yang sudah di-test"""
        tested_zones = []
        
        for zone in analysis['supply_zones'] + analysis['demand_zones']:
            zone_low = min(zone['price_range'])
            zone_high = max(zone['price_range'])
            
            # Count tests on this zone
            zone_tests = df[
                (df['low'] <= zone_high) & 
                (df['high'] >= zone_low)
            ]
            
            if len(zone_tests) > 1:  # More than just the creation candle
                zone['test_count'] = len(zone_tests)
                zone['last_test'] = zone_tests.iloc[-1]['timestamp']
                tested_zones.append(zone)
                
        return tested_zones
        
    def _calculate_zone_quality(self, analysis):
        """Hitung kualitas zona secara keseluruhan"""
        total_zones = len(analysis['supply_zones']) + len(analysis['demand_zones'])
        if total_zones == 0:
            return 0.0
            
        fresh_ratio = len(analysis['fresh_zones']) / total_zones
        strong_zones = len([z for z in analysis['supply_zones'] + analysis['demand_zones'] if z['strength'] == 'strong'])
        strong_ratio = strong_zones / total_zones
        
        return (fresh_ratio * 0.6 + strong_ratio * 0.4)
