"""
PRICE ACTION ENGINE - Analisis struktur candle & momentum
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class PriceActionEngine:
    def __init__(self):
        self.setup_candle_patterns()
        
    def setup_candle_patterns(self):
        """Setup pola candle"""
        self.bullish_patterns = ['hammer', 'bullish_engulfing', 'morning_star']
        self.bearish_patterns = ['shooting_star', 'bearish_engulfing', 'evening_star']
        
    async def initialize(self):
        """Initialize price action engine"""
        logging.info("🕯️ INITIALIZING PRICE ACTION ENGINE...")
        
    async def analyze(self, market_data, structure_analysis):
        """Analisis price action"""
        pa_analysis = {}
        
        for pair, data in market_data.items():
            try:
                analysis = await self._analyze_pair_pa(pair, data, structure_analysis.get(pair, {}))
                pa_analysis[pair] = analysis
            except Exception as e:
                logging.error(f"❌ Price action analysis error for {pair}: {e}")
                continue
                
        return pa_analysis
        
    async def _analyze_pair_pa(self, pair, data, structure_data):
        """Analisis price action untuk satu pair"""
        analysis = {
            'candle_patterns': [],
            'momentum_indicators': {},
            'support_resistance': [],
            'key_rejections': [],
            'consolidation_zones': [],
            'breakout_signals': [],
            'pa_strength': 'neutral'
        }
        
        if len(data) < 20:
            return analysis
            
        df = pd.DataFrame(data)
        
        # 1. Candle Pattern Recognition
        analysis['candle_patterns'] = self._find_candle_patterns(df)
        
        # 2. Momentum Indicators
        analysis['momentum_indicators'] = self._calculate_momentum(df)
        
        # 3. Support Resistance
        analysis['support_resistance'] = self._find_support_resistance(df)
        
        # 4. Key Rejections
        analysis['key_rejections'] = self._find_key_rejections(df)
        
        # 5. Consolidation Zones
        analysis['consolidation_zones'] = self._find_consolidation_zones(df)
        
        # 6. Breakout Signals
        analysis['breakout_signals'] = self._find_breakout_signals(df)
        
        # 7. Price Action Strength
        analysis['pa_strength'] = self._analyze_pa_strength(analysis)
        
        return analysis
        
    def _find_candle_patterns(self, df):
        """Temukan pola candle"""
        patterns = []
        
        for i in range(2, len(df)-1):
            patterns_found = self._analyze_single_candle(df, i)
            patterns.extend(patterns_found)
            
        return patterns
        
    def _analyze_single_candle(self, df, index):
        """Analisis satu candle untuk pola"""
        patterns = []
        candle = df.iloc[index]
        prev_candle = df.iloc[index-1]
        
        body_size = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        upper_wick = candle['high'] - max(candle['open'], candle['close'])
        lower_wick = min(candle['open'], candle['close']) - candle['low']
        
        # Hammer pattern
        if (lower_wick > body_size * 2 and 
            upper_wick < body_size * 0.5 and
            total_range > df['high'].iloc[index-10:index].std()):
            patterns.append({
                'type': 'hammer',
                'timestamp': candle['timestamp'],
                'strength': 'medium',
                'direction': 'bullish'
            })
            
        # Shooting star
        if (upper_wick > body_size * 2 and
            lower_wick < body_size * 0.5 and
            total_range > df['high'].iloc[index-10:index].std()):
            patterns.append({
                'type': 'shooting_star',
                'timestamp': candle['timestamp'], 
                'strength': 'medium',
                'direction': 'bearish'
            })
            
        # Engulfing patterns
        if (abs(prev_candle['close'] - prev_candle['open']) < body_size and
            ((candle['close'] > prev_candle['high'] and candle['open'] < prev_candle['low']) or
             (candle['close'] < prev_candle['low'] and candle['open'] > prev_candle['high']))):
            
            direction = 'bullish' if candle['close'] > candle['open'] else 'bearish'
            patterns.append({
                'type': f'{direction}_engulfing',
                'timestamp': candle['timestamp'],
                'strength': 'strong',
                'direction': direction
            })
            
        return patterns
        
    def _calculate_momentum(self, df):
        """Hitung indikator momentum"""
        momentum = {
            'rsi': 50,
            'stochastic': 50,
            'macd': 0,
            'momentum_score': 0.5
        }
        
        prices = df['close'].values
        
        # RSI Calculation
        if len(prices) >= 14:
            gains = np.where(np.diff(prices) > 0, np.diff(prices), 0)
            losses = np.where(np.diff(prices) < 0, -np.diff(prices), 0)
            
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                
            momentum['rsi'] = rsi
            
        # Stochastic (simplified)
        if len(prices) >= 14:
            high_14 = max(df['high'].iloc[-14:])
            low_14 = min(df['low'].iloc[-14:])
            current_close = prices[-1]
            
            if high_14 != low_14:
                stoch = (current_close - low_14) / (high_14 - low_14) * 100
                momentum['stochastic'] = stoch
                
        # MACD (simplified)
        if len(prices) >= 26:
            ema_12 = pd.Series(prices).ewm(span=12).mean().iloc[-1]
            ema_26 = pd.Series(prices).ewm(span=26).mean().iloc[-1]
            momentum['macd'] = ema_12 - ema_26
            
        # Momentum Score
        rsi_score = 1 - abs(momentum['rsi'] - 50) / 50  # Closer to 50 is better
        stoch_score = 1 - abs(momentum['stochastic'] - 50) / 50
        momentum['momentum_score'] = (rsi_score + stoch_score) / 2
        
        return momentum
        
    def _find_support_resistance(self, df):
        """Temukan support resistance dinamis"""
        levels = []
        prices = df['close'].values
        
        # Find recent swing points
        for i in range(10, len(prices)-10):
            if (prices[i] == max(prices[i-10:i+10])):  # Swing high
                levels.append({
                    'price': prices[i],
                    'type': 'resistance',
                    'strength': 'medium',
                    'timestamp': df.iloc[i]['timestamp']
                })
            elif (prices[i] == min(prices[i-10:i+10])):  # Swing low
                levels.append({
                    'price': prices[i],
                    'type': 'support', 
                    'strength': 'medium',
                    'timestamp': df.iloc[i]['timestamp']
                })
                
        return levels
        
    def _find_key_rejections(self, df):
        """Temukan penolakan kunci (rejection candles)"""
        rejections = []
        
        for i in range(2, len(df)-1):
            candle = df.iloc[i]
            body_size = abs(candle['close'] - candle['open'])
            total_range = candle['high'] - candle['low']
            
            # Strong rejection: small body, large wick
            if body_size / total_range < 0.3:
                upper_wick = candle['high'] - max(candle['open'], candle['close'])
                lower_wick = min(candle['open'], candle['close']) - candle['low']
                
                if upper_wick > lower_wick * 2:  # Upper rejection
                    rejections.append({
                        'price': candle['high'],
                        'type': 'resistance_rejection',
                        'strength': 'strong',
                        'timestamp': candle['timestamp']
                    })
                elif lower_wick > upper_wick * 2:  # Lower rejection
                    rejections.append({
                        'price': candle['low'],
                        'type': 'support_rejection',
                        'strength': 'strong', 
                        'timestamp': candle['timestamp']
                    })
                    
        return rejections
        
    def _find_consolidation_zones(self, df):
        """Temukan zona konsolidasi"""
        zones = []
        window_size = 10
        
        for i in range(window_size, len(df)-window_size):
            window = df.iloc[i-window_size:i]
            volatility = (window['high'].max() - window['low'].min()) / window['close'].mean()
            
            if volatility < 0.02:  # Low volatility = consolidation
                zones.append({
                    'price_range': [window['low'].min(), window['high'].max()],
                    'duration': window_size,
                    'type': 'consolidation',
                    'timestamp': df.iloc[i]['timestamp']
                })
                
        return zones
        
    def _find_breakout_signals(self, df):
        """Temukan sinyal breakout"""
        breakouts = []
        
        # Check for breakouts from consolidation
        consolidation_zones = self._find_consolidation_zones(df)
        
        for zone in consolidation_zones[-3:]:  # Check recent zones
            zone_high = zone['price_range'][1]
            zone_low = zone['price_range'][0]
            
            recent_close = df['close'].iloc[-1]
            prev_close = df['close'].iloc[-2]
            
            # Breakout above
            if recent_close > zone_high and prev_close <= zone_high:
                breakouts.append({
                    'price': recent_close,
                    'type': 'bullish_breakout',
                    'strength': 'medium',
                    'timestamp': df.iloc[-1]['timestamp']
                })
                
            # Breakout below
            elif recent_close < zone_low and prev_close >= zone_low:
                breakouts.append({
                    'price': recent_close,
                    'type': 'bearish_breakout',
                    'strength': 'medium',
                    'timestamp': df.iloc[-1]['timestamp']
                })
                
        return breakouts
        
    def _analyze_pa_strength(self, analysis):
        """Analisis strength price action"""
        bullish_signals = len([p for p in analysis['candle_patterns'] if p['direction'] == 'bullish'])
        bearish_signals = len([p for p in analysis['candle_patterns'] if p['direction'] == 'bearish'])
        
        momentum = analysis['momentum_indicators'].get('momentum_score', 0.5)
        
        if bullish_signals > bearish_signals and momentum > 0.6:
            return "bullish"
        elif bearish_signals > bullish_signals and momentum < 0.4:
            return "bearish"
        else:
            return "neutral"
