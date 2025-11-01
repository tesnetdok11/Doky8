"""
MARKET STRUCTURE ENGINE - Analisis BOS, CHoCH, Liquidity Map
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketStructureEngine:
    def __init__(self):
        self.setup_indicators()
        
    def setup_indicators(self):
        """Setup indikator analisis struktur"""
        self.required_data_points = 100
        
    async def initialize(self):
        """Initialize market structure engine"""
        logging.info("🏗️ INITIALIZING MARKET STRUCTURE ENGINE...")
        
    async def analyze(self, tf_data):
        """Analisis struktur pasar untuk semua pairs dan timeframes"""
        structure_analysis = {}
        
        for pair, timeframes in tf_data.items():
            try:
                analysis = await self._analyze_pair(pair, timeframes)
                structure_analysis[pair] = analysis
            except Exception as e:
                logging.error(f"❌ Structure analysis error for {pair}: {e}")
                continue
                
        return structure_analysis
        
    async def _analyze_pair(self, pair, timeframes):
        """Analisis struktur untuk satu pair"""
        analysis = {
            'trend_direction': 'neutral',
            'trend_strength': 0.0,
            'key_levels': [],
            'liquidity_zones': [],
            'bos_confirmed': False,
            'choch_confirmed': False,
            'price_action': {},
            'volume_analysis': {},
            'momentum': {},
            'volatility': 'medium',
            'primary_tf': '15m'
        }
        
        # Analisis untuk setiap timeframe
        for tf, data in timeframes.items():
            if len(data) < self.required_data_points:
                continue
                
            tf_analysis = await self._analyze_timeframe(data)
            analysis.update(tf_analysis)
            
        # Tentukan trend utama berdasarkan multi timeframe
        analysis['trend_direction'] = self._determine_primary_trend(analysis)
        analysis['trend_strength'] = self._calculate_trend_strength(analysis)
        analysis['volatility'] = self._calculate_volatility(analysis)
        
        return analysis
        
    async def _analyze_timeframe(self, data):
        """Analisis struktur untuk satu timeframe"""
        df = pd.DataFrame(data)
        analysis = {}
        
        # Identifikasi Higher Highs/Lower Lows
        highs = df['high'].values
        lows = df['low'].values
        
        # Break of Structure (BOS)
        bos = self._detect_bos(highs, lows)
        analysis['bos_confirmed'] = bos
        
        # Change of Character (CHoCH)
        choch = self._detect_choch(highs, lows)
        analysis['choch_confirmed'] = choch
        
        # Key levels (Support/Resistance)
        analysis['key_levels'] = self._find_key_levels(highs, lows)
        
        # Liquidity zones
        analysis['liquidity_zones'] = self._find_liquidity_zones(df)
        
        # Price action
        analysis['price_action'] = self._analyze_price_action(df)
        
        # Volume analysis
        analysis['volume_analysis'] = self._analyze_volume(df)
        
        # Momentum
        analysis['momentum'] = self._analyze_momentum(df)
        
        return analysis
        
    def _detect_bos(self, highs, lows):
        """Deteksi Break of Structure"""
        if len(highs) < 20:
            return False
            
        # Logic BOS: Higher high setelah sequence lower highs
        recent_high = highs[-1]
        prev_highs = highs[-10:-1]
        
        if recent_high > max(prev_highs):
            return True
            
        return False
        
    def _detect_choch(self, highs, lows):
        """Deteksi Change of Character"""
        if len(highs) < 20:
            return False
            
        # Logic CHoCH: Pola reversal
        recent_trend = self._get_trend_direction(highs[-5:], lows[-5:])
        previous_trend = self._get_trend_direction(highs[-10:-5], lows[-10:-5])
        
        if recent_trend != previous_trend and recent_trend != 'neutral':
            return True
            
        return False
        
    def _find_key_levels(self, highs, lows):
        """Temukan level support/resistance kunci"""
        # Simplified key levels detection
        resistance = max(highs[-20:])
        support = min(lows[-20:])
        
        return [
            {'level': support, 'type': 'support', 'strength': 'strong'},
            {'level': resistance, 'type': 'resistance', 'strength': 'strong'}
        ]
        
    def _find_liquidity_zones(self, df):
        """Temukan zona liquidity"""
        # Simplified liquidity zones
        zones = []
        
        # High liquidity di area high/low
        zones.append({
            'price': df['high'].max(),
            'type': 'liquidity_pool',
            'timeframe': 'multiple'
        })
        
        zones.append({
            'price': df['low'].min(), 
            'type': 'liquidity_pool',
            'timeframe': 'multiple'
        })
        
        return zones
        
    def _analyze_price_action(self, df):
        """Analisis price action"""
        recent = df.iloc[-5:]
        
        return {
            'open': recent['open'].iloc[-1],
            'high': recent['high'].max(),
            'low': recent['low'].min(),
            'close': recent['close'].iloc[-1],
            'body_ratio': abs(recent['close'] - recent['open']).mean() / (recent['high'] - recent['low']).mean()
        }
        
    def _analyze_volume(self, df):
        """Analisis volume"""
        if 'volume' not in df.columns:
            return {}
            
        recent_volume = df['volume'].iloc[-10:].mean()
        prev_volume = df['volume'].iloc[-20:-10].mean()
        
        return {
            'volume_trend': 'increasing' if recent_volume > prev_volume else 'decreasing',
            'volume_spike': recent_volume > prev_volume * 1.5,
            'delta_positive': True  # Simplified
        }
        
    def _analyze_momentum(self, df):
        """Analisis momentum"""
        prices = df['close'].values
        
        if len(prices) < 14:
            return {}
            
        # Simplified RSI calculation
        gains = np.where(np.diff(prices) > 0, np.diff(prices), 0)
        losses = np.where(np.diff(prices) < 0, -np.diff(prices), 0)
        
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
        return {
            'rsi': rsi,
            'momentum': 'bullish' if rsi > 50 else 'bearish'
        }
        
    def _get_trend_direction(self, highs, lows):
        """Tentukan arah trend"""
        if len(highs) < 2:
            return 'neutral'
            
        high_trend = 'up' if highs[-1] > highs[0] else 'down'
        low_trend = 'up' if lows[-1] > lows[0] else 'down'
        
        if high_trend == 'up' and low_trend == 'up':
            return 'bullish'
        elif high_trend == 'down' and low_trend == 'down':
            return 'bearish'
        else:
            return 'neutral'
            
    def _determine_primary_trend(self, analysis):
        """Tentukan trend utama berdasarkan multi timeframe"""
        # Simplified - dalam implementasi nyata akan lebih kompleks
        return analysis.get('trend_direction', 'neutral')
        
    def _calculate_trend_strength(self, analysis):
        """Hitung kekuatan trend"""
        # Simplified
        return 0.7  # Placeholder
        
    def _calculate_volatility(self, analysis):
        """Hitung volatilitas"""
        price_data = analysis.get('price_action', {})
        high = price_data.get('high', 0)
        low = price_data.get('low', 0)
        close = price_data.get('close', 0)
        
        if high == 0:
            return 'medium'
            
        volatility_ratio = (high - low) / close
        
        if volatility_ratio > 0.05:
            return 'high'
        elif volatility_ratio < 0.01:
            return 'low'
        else:
            return 'medium'
