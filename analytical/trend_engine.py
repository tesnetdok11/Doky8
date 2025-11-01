"""
TREND ENGINE - Analisa arah tren & reversal
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TrendEngine:
    def __init__(self):
        self.setup_trend_models()
        
    def setup_trend_models(self):
        """Setup model trend analysis"""
        self.trend_periods = {
            'short_term': 20,
            'medium_term': 50, 
            'long_term': 100
        }
        
    async def initialize(self):
        """Initialize trend engine"""
        logging.info("📈 INITIALIZING TREND ENGINE...")
        
    async def analyze(self, market_data, structure_analysis):
        """Analisis trend untuk semua pairs"""
        trend_analysis = {}
        
        for pair, data in market_data.items():
            try:
                analysis = await self._analyze_pair_trend(pair, data, structure_analysis.get(pair, {}))
                trend_analysis[pair] = analysis
            except Exception as e:
                logging.error(f"❌ Trend analysis error for {pair}: {e}")
                continue
                
        return trend_analysis
        
    async def _analyze_pair_trend(self, pair, data, structure_data):
        """Analisis trend untuk satu pair"""
        analysis = {
            'primary_trend': 'neutral',
            'trend_strength': 0.0,
            'trend_duration': 0,
            'momentum': 'neutral',
            'reversal_signals': [],
            'trend_lines': [],
            'multiple_timeframe_alignment': {},
            'volatility_regime': 'normal'
        }
        
        if len(data) < 100:
            return analysis
            
        df = pd.DataFrame(data)
        
        # 1. Primary Trend Analysis
        analysis['primary_trend'] = self._determine_primary_trend(df)
        
        # 2. Trend Strength
        analysis['trend_strength'] = self._calculate_trend_strength(df)
        
        # 3. Trend Duration
        analysis['trend_duration'] = self._calculate_trend_duration(df)
        
        # 4. Momentum Analysis
        analysis['momentum'] = self._analyze_momentum(df)
        
        # 5. Reversal Signals
        analysis['reversal_signals'] = self._find_reversal_signals(df)
        
        # 6. Trend Lines
        analysis['trend_lines'] = self._calculate_trend_lines(df)
        
        # 7. Multi-Timeframe Alignment
        analysis['multiple_timeframe_alignment'] = self._analyze_mtf_alignment(df)
        
        # 8. Volatility Regime
        analysis['volatility_regime'] = self._determine_volatility_regime(df)
        
        return analysis
        
    def _determine_primary_trend(self, df):
        """Tentukan trend utama"""
        prices = df['close'].values
        
        # Multiple timeframe analysis
        short_ma = pd.Series(prices).rolling(window=20).mean().iloc[-1]
        medium_ma = pd.Series(prices).rolling(window=50).mean().iloc[-1]
        long_ma = pd.Series(prices).rolling(window=100).mean().iloc[-1]
        
        # Trend determination
        if short_ma > medium_ma > long_ma:
            return "bullish"
        elif short_ma < medium_ma < long_ma:
            return "bearish"
        else:
            return "neutral"
            
    def _calculate_trend_strength(self, df):
        """Hitung kekuatan trend"""
        prices = df['close'].values
        
        if len(prices) < 20:
            return 0.0
            
        # ADX-like strength calculation (simplified)
        highs = df['high'].values
        lows = df['low'].values
        
        # Average True Range
        tr_values = []
        for i in range(1, len(prices)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - prices[i-1])
            tr3 = abs(lows[i] - prices[i-1])
            tr_values.append(max(tr1, tr2, tr3))
            
        atr = np.mean(tr_values[-14:]) if tr_values else 0
        
        # Directional Movement
        plus_dm = 0
        minus_dm = 0
        
        for i in range(1, len(prices)):
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]
            
            if up_move > down_move and up_move > 0:
                plus_dm += up_move
            elif down_move > up_move and down_move > 0:
                minus_dm += down_move
                
        # Strength calculation
        if atr > 0:
            strength = (abs(plus_dm - minus_dm) / atr) / len(prices)
            return min(strength * 100, 1.0)  # Normalize to 0-1
        else:
            return 0.0
            
    def _calculate_trend_duration(self, df):
        """Hitung durasi trend saat ini"""
        prices = df['close'].values
        current_trend = self._determine_primary_trend(df)
        
        # Count how long the current trend has persisted
        duration = 0
        for i in range(len(prices)-1, 0, -1):
            window = prices[max(0, i-20):i+1]
            if len(window) < 10:
                break
                
            window_trend = self._determine_trend_for_window(window)
            if window_trend == current_trend:
                duration += 1
            else:
                break
                
        return duration
        
    def _determine_trend_for_window(self, prices):
        """Tentukan trend untuk window tertentu"""
        if len(prices) < 10:
            return "neutral"
            
        short_avg = np.mean(prices[-5:])
        long_avg = np.mean(prices[-10:])
        
        if short_avg > long_avg * 1.01:
            return "bullish"
        elif short_avg < long_avg * 0.99:
            return "bearish"
        else:
            return "neutral"
            
    def _analyze_momentum(self, df):
        """Analisis momentum trend"""
        prices = df['close'].values
        
        if len(prices) < 14:
            return "neutral"
            
        # RSI momentum
        gains = np.where(np.diff(prices) > 0, np.diff(prices), 0)
        losses = np.where(np.diff(prices) < 0, -np.diff(prices), 0)
        
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
        # Momentum classification
        if rsi > 70:
            return "overbought"
        elif rsi < 30:
            return "oversold"
        elif rsi > 55:
            return "bullish"
        elif rsi < 45:
            return "bearish"
        else:
            return "neutral"
            
    def _find_reversal_signals(self, df):
        """Temukan sinyal reversal"""
        signals = []
        prices = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        
        # Divergence detection (simplified)
        if len(prices) >= 30:
            # Price making higher high but indicator not confirming
            if (highs[-1] > highs[-2] and highs[-2] > highs[-3] and
                prices[-1] < prices[-5]):  # Price weakness
                signals.append({
                    'type': 'bearish_divergence',
                    'strength': 'medium',
                    'timestamp': df.iloc[-1]['timestamp']
                })
                
            # Price making lower low but indicator not confirming
            if (lows[-1] < lows[-2] and lows[-2] < lows[-3] and
                prices[-1] > prices[-5]):  # Price strength
                signals.append({
                    'type': 'bullish_divergence',
                    'strength': 'medium',
                    'timestamp': df.iloc[-1]['timestamp']
                })
                
        # Trend line break
        trend_lines = self._calculate_trend_lines(df)
        for tl in trend_lines:
            if (tl['type'] == 'support' and prices[-1] < tl['price'] and
                prices[-2] >= tl['price']):
                signals.append({
                    'type': 'support_break',
                    'strength': 'strong',
                    'timestamp': df.iloc[-1]['timestamp']
                })
                
        return signals
        
    def _calculate_trend_lines(self, df):
        """Hitung garis trend"""
        trend_lines = []
        prices = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        
        # Simplified trend line calculation
        # Support line from recent lows
        recent_lows = lows[-10:]
        if len(recent_lows) >= 3:
            support_level = min(recent_lows)
            trend_lines.append({
                'price': support_level,
                'type': 'support',
                'strength': 'medium'
            })
            
        # Resistance line from recent highs
        recent_highs = highs[-10:]
        if len(recent_highs) >= 3:
            resistance_level = max(recent_highs)
            trend_lines.append({
                'price': resistance_level,
                'type': 'resistance', 
                'strength': 'medium'
            })
            
        return trend_lines
        
    def _analyze_mtf_alignment(self, df):
        """Analisis alignment multiple timeframe"""
        alignment = {
            'aligned': False,
            'direction': 'neutral',
            'timeframes_aligned': 0,
            'alignment_score': 0.0
        }
        
        # Simplified MTF analysis using different window sizes
        timeframes = {
            'short': 20,
            'medium': 50,
            'long': 100
        }
        
        prices = df['close'].values
        trends = []
        
        for tf_name, window in timeframes.items():
            if len(prices) >= window:
                tf_trend = self._determine_trend_for_window(prices[-window:])
                trends.append(tf_trend)
                
        # Count aligned timeframes
        bullish_count = trends.count('bullish')
        bearish_count = trends.count('bearish')
        
        total_tfs = len(trends)
        if total_tfs > 0:
            max_count = max(bullish_count, bearish_count)
            alignment_score = max_count / total_tfs
            
            alignment['alignment_score'] = alignment_score
            alignment['timeframes_aligned'] = max_count
            
            if alignment_score >= 0.67:  # 2/3 alignment
                alignment['aligned'] = True
                alignment['direction'] = 'bullish' if bullish_count > bearish_count else 'bearish'
                
        return alignment
        
    def _determine_volatility_regime(self, df):
        """Tentukan regime volatilitas"""
        prices = df['close'].values
        
        if len(prices) < 20:
            return "normal"
            
        # Calculate volatility (standard deviation of returns)
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) * np.sqrt(365)  # Annualized
        
        if volatility > 0.8:  # 80% annualized volatility
            return "high"
        elif volatility < 0.2:  # 20% annualized volatility
            return "low"
        else:
            return "normal"
