"""
VOLUME ANALYZER - Analisa OI, CVD, Delta Volume
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class VolumeAnalyzer:
    def __init__(self):
        self.setup_volume_models()
        
    def setup_volume_models(self):
        """Setup model analisis volume"""
        self.volume_profile = {}
        self.delta_values = {}
        self.oi_analysis = {}
    
    async def enhance_with_aggr_data(self, volume_analysis, aggr_data, pair):
        """Enhance volume analysis with aggregated trade data"""
        try:
            if not aggr_data or not aggr_data.get('data'):
                return volume_analysis
                
            enhanced_analysis = volume_analysis.copy()
            
            # Add Aggr-specific volume metrics
            aggr_metrics = await self._calculate_aggr_volume_metrics(aggr_data)
            enhanced_analysis['aggr_enhanced'] = aggr_metrics
            
            # Update volume trend with Aggr data
            if aggr_metrics.get('trade_flow_imbalance'):
                imbalance = aggr_metrics['trade_flow_imbalance']
                if abs(imbalance) > 0.2:
                    enhanced_analysis['volume_trend'] = 'strong_buying' if imbalance > 0 else 'strong_selling'
                    
            return enhanced_analysis
            
        except Exception as e:
            logging.error(f"❌ Aggr volume enhancement error for {pair}: {e}")
            return volume_analysis
            
    async def _calculate_aggr_volume_metrics(self, aggr_data):
        """Calculate advanced volume metrics from Aggr data"""
        try:
            df = pd.DataFrame(aggr_data['data'])
            
            metrics = {
                'total_aggr_volume': df['volume'].sum(),
                'avg_trade_size': df['volume'].mean(),
                'large_trade_ratio': len(df[df['volume'] > df['volume'].quantile(0.9)]) / len(df),
                'volume_concentration': df['volume'].std() / df['volume'].mean()
            }
            
            # Trade flow analysis
            if 'estimated_side' in df.columns:
                buy_volume = df[df['estimated_side'] == 'buy']['volume'].sum()
                sell_volume = df[df['estimated_side'] == 'sell']['volume'].sum()
                metrics['trade_flow_imbalance'] = (buy_volume - sell_volume) / (buy_volume + sell_volume)
                
            return metrics
            
        except Exception as e:
            logging.error(f"❌ Aggr volume metrics calculation error: {e}")
            return {}        
    async def initialize(self):
        """Initialize volume analyzer"""
        logging.info("📊 INITIALIZING VOLUME ANALYZER...")
        
    async def analyze(self, market_data, structure_analysis):
        """Analisis volume dan OI"""
        volume_analysis = {}
        
        for pair, data in market_data.items():
            try:
                analysis = await self._analyze_pair_volume(pair, data, structure_analysis.get(pair, {}))
                volume_analysis[pair] = analysis
            except Exception as e:
                logging.error(f"❌ Volume analysis error for {pair}: {e}")
                continue
                
        return volume_analysis
        
    async def _analyze_pair_volume(self, pair, data, structure_data):
        """Analisis volume untuk satu pair"""
        analysis = {
            'volume_profile': {},
            'delta_analysis': {},
            'oi_analysis': {},
            'cvd_analysis': {},
            'volume_clusters': [],
            'volume_zones': [],
            'volume_trend': 'neutral',
            'accumulation_distribution': 'neutral'
        }
        
        if len(data) < 50:
            return analysis
            
        df = pd.DataFrame(data)
        
        # 1. Volume Profile Analysis
        analysis['volume_profile'] = self._analyze_volume_profile(df)
        
        # 2. Delta Analysis
        analysis['delta_analysis'] = self._analyze_delta(df)
        
        # 3. Open Interest Analysis
        analysis['oi_analysis'] = self._analyze_oi(df)
        
        # 4. CVD Analysis
        analysis['cvd_analysis'] = self._analyze_cvd(df)
        
        # 5. Volume Clusters
        analysis['volume_clusters'] = self._find_volume_clusters(df)
        
        # 6. Volume Zones
        analysis['volume_zones'] = self._find_volume_zones(df)
        
        # 7. Volume Trend
        analysis['volume_trend'] = self._analyze_volume_trend(df)
        
        # 8. Accumulation/Distribution
        analysis['accumulation_distribution'] = self._analyze_accumulation(df)
        
        return analysis
        
    def _analyze_volume_profile(self, df):
        """Analisis volume profile"""
        profile = {
            'poc': 0,  # Point of Control
            'value_area_high': 0,
            'value_area_low': 0,
            'volume_delta': 0,
            'profile_balance': 'neutral'
        }
        
        if 'volume' not in df.columns:
            return profile
            
        # Simplified Volume Profile
        price_levels = np.linspace(df['low'].min(), df['high'].max(), 20)
        volume_at_price = {}
        
        for level in price_levels:
            # Volume near this price level
            nearby_volume = df[
                (df['low'] <= level) & (df['high'] >= level)
            ]['volume'].sum()
            volume_at_price[level] = nearby_volume
            
        if volume_at_price:
            poc_price = max(volume_at_price, key=volume_at_price.get)
            profile['poc'] = poc_price
            
            # Value Area (70% of volume)
            total_volume = sum(volume_at_price.values())
            sorted_prices = sorted(volume_at_price.items(), key=lambda x: x[1], reverse=True)
            
            cumulative_volume = 0
            value_area_prices = []
            
            for price, volume in sorted_prices:
                cumulative_volume += volume
                value_area_prices.append(price)
                if cumulative_volume >= total_volume * 0.7:
                    break
                    
            profile['value_area_high'] = max(value_area_prices)
            profile['value_area_low'] = min(value_area_prices)
            
        return profile
        
    def _analyze_delta(self, df):
        """Analisis volume delta (buy vs sell volume)"""
        delta_analysis = {
            'total_delta': 0,
            'delta_trend': 'neutral',
            'large_orders': 0,
            'delta_divergence': False
        }
        
        if 'volume' not in df.columns:
            return delta_analysis
            
        # Simplified delta calculation
        buy_volume = 0
        sell_volume = 0
        
        for i in range(len(df)):
            candle = df.iloc[i]
            # Assume: if close > open, more buying pressure
            if candle['close'] > candle['open']:
                buy_volume += candle['volume']
            else:
                sell_volume += candle['volume']
                
        total_delta = buy_volume - sell_volume
        delta_analysis['total_delta'] = total_delta
        
        # Delta trend
        if total_delta > df['volume'].mean() * 0.1:
            delta_analysis['delta_trend'] = 'positive'
        elif total_delta < -df['volume'].mean() * 0.1:
            delta_analysis['delta_trend'] = 'negative'
            
        # Large orders (volume spikes)
        avg_volume = df['volume'].mean()
        large_orders = len(df[df['volume'] > avg_volume * 2])
        delta_analysis['large_orders'] = large_orders
        
        return delta_analysis
        
    def _analyze_oi(self, df):
        """Analisis Open Interest"""
        oi_analysis = {
            'oi_trend': 'neutral',
            'oi_breakdown': {},
            'funding_impact': 'neutral'
        }
        
        # Simplified OI analysis
        if 'open_interest' in df.columns:
            recent_oi = df['open_interest'].iloc[-10:].mean()
            previous_oi = df['open_interest'].iloc[-20:-10].mean()
            
            if recent_oi > previous_oi * 1.1:
                oi_analysis['oi_trend'] = 'increasing'
            elif recent_oi < previous_oi * 0.9:
                oi_analysis['oi_trend'] = 'decreasing'
                
        return oi_analysis
        
    def _analyze_cvd(self, df):
        """Analisis Cumulative Volume Delta"""
        cvd_analysis = {
            'cvd_value': 0,
            'cvd_trend': 'neutral',
            'cvd_divergence': False
        }
        
        if 'volume' not in df.columns:
            return cvd_analysis
            
        # Calculate CVD
        cvd = 0
        cvd_values = []
        
        for i in range(len(df)):
            candle = df.iloc[i]
            if candle['close'] > candle['open']:
                cvd += candle['volume']  # Buying pressure
            else:
                cvd -= candle['volume']  # Selling pressure
            cvd_values.append(cvd)
            
        cvd_analysis['cvd_value'] = cvd
            
        # CVD trend
        if len(cvd_values) >= 10:
            recent_cvd = cvd_values[-5:]
            previous_cvd = cvd_values[-10:-5]
            
            if np.mean(recent_cvd) > np.mean(previous_cvd):
                cvd_analysis['cvd_trend'] = 'bullish'
            else:
                cvd_analysis['cvd_trend'] = 'bearish'
                
        return cvd_analysis
        
    def _find_volume_clusters(self, df):
        """Temukan cluster volume tinggi"""
        clusters = []
        
        if 'volume' not in df.columns:
            return clusters
            
        avg_volume = df['volume'].mean()
        std_volume = df['volume'].std()
        
        for i in range(len(df)):
            volume = df.iloc[i]['volume']
            if volume > avg_volume + std_volume:
                clusters.append({
                    'price': df.iloc[i]['close'],
                    'volume': volume,
                    'timestamp': df.iloc[i]['timestamp'],
                    'type': 'volume_spike'
                })
                
        return clusters
        
    def _find_volume_zones(self, df):
        """Temukan zona volume tinggi"""
        zones = []
        
        if 'volume' not in df.columns:
            return zones
            
        # Look for consecutive high volume candles
        high_volume_threshold = df['volume'].mean() * 1.5
        
        current_zone = None
        for i in range(len(df)):
            if df.iloc[i]['volume'] > high_volume_threshold:
                if current_zone is None:
                    current_zone = {
                        'start_index': i,
                        'end_index': i,
                        'total_volume': df.iloc[i]['volume'],
                        'price_range': [df.iloc[i]['low'], df.iloc[i]['high']]
                    }
                else:
                    current_zone['end_index'] = i
                    current_zone['total_volume'] += df.iloc[i]['volume']
                    current_zone['price_range'][0] = min(current_zone['price_range'][0], df.iloc[i]['low'])
                    current_zone['price_range'][1] = max(current_zone['price_range'][1], df.iloc[i]['high'])
            else:
                if current_zone is not None and (current_zone['end_index'] - current_zone['start_index']) >= 2:
                    zones.append({
                        'price_range': current_zone['price_range'],
                        'total_volume': current_zone['total_volume'],
                        'duration': current_zone['end_index'] - current_zone['start_index'] + 1,
                        'type': 'high_volume_zone'
                    })
                current_zone = None
                
        return zones
        
    def _analyze_volume_trend(self, df):
        """Analisis trend volume"""
        if 'volume' not in df.columns:
            return 'neutral'
            
        recent_volume = df['volume'].iloc[-10:].mean()
        previous_volume = df['volume'].iloc[-20:-10].mean()
        
        if recent_volume > previous_volume * 1.2:
            return 'increasing'
        elif recent_volume < previous_volume * 0.8:
            return 'decreasing'
        else:
            return 'neutral'
            
    def _analyze_accumulation(self, df):
        """Analisis akumulasi vs distribusi"""
        if 'volume' not in df.columns:
            return 'neutral'
            
        # Price and volume relationship
        price_trend = 'up' if df['close'].iloc[-1] > df['close'].iloc[-10] else 'down'
        volume_trend = self._analyze_volume_trend(df)
        
        if price_trend == 'up' and volume_trend == 'increasing':
            return 'accumulation'
        elif price_trend == 'down' and volume_trend == 'increasing':
            return 'distribution'
        else:
            return 'neutral'
