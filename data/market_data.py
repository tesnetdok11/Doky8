"""
MARKET DATA - Loader data OHLCV terstandarisasi
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config.pairs import TOP_25_PAIRS

class MarketData:
    def __init__(self):
        self.data_cache = {}
        self.cache_duration = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize market data system"""
        logging.info("📈 INITIALIZING MARKET DATA SYSTEM...")
        
    async def load_ohlcv_data(self, exchange_data, primary_exchange='binance'):
        """Load and standardize OHLCV data from exchange"""
        standardized_data = {}
        
        try:
            for pair in TOP_25_PAIRS:
                if pair in exchange_data:
                    exchange_info = exchange_data[pair]
                    standardized_data[pair] = await self._standardize_pair_data(
                        exchange_info, primary_exchange
                    )
                    
            logging.info(f"✅ Loaded OHLCV data for {len(standardized_data)} pairs")
            return standardized_data
            
        except Exception as e:
            logging.error(f"❌ OHLCV data loading error: {e}")
            return {}
            
    async def _standardize_pair_data(self, exchange_info, primary_exchange):
        """Standardize data for a single pair"""
        try:
            standardized = {
                'pair': exchange_info.get('pair', ''),
                'exchange': exchange_info.get('exchange', primary_exchange),
                'current_price': exchange_info.get('current_price', 0),
                'price_change_24h': exchange_info.get('price_change_24h', 0),
                'price_change_percent_24h': exchange_info.get('price_change_percent_24h', 0),
                'volume_24h': exchange_info.get('volume_24h', 0),
                'high_24h': exchange_info.get('high_24h', 0),
                'low_24h': exchange_info.get('low_24h', 0),
                'timestamp': exchange_info.get('timestamp', datetime.utcnow()),
                'ohlcv': {}
            }
            
            # Standardize OHLCV data for each timeframe
            ohlcv_data = exchange_info.get('ohlcv', {})
            for timeframe, candles in ohlcv_data.items():
                if candles:
                    standardized['ohlcv'][timeframe] = self._standardize_candles(
                        candles, timeframe
                    )
                    
            return standardized
            
        except Exception as e:
            logging.error(f"❌ Pair data standardization error: {e}")
            return None
            
    def _standardize_candles(self, candles, timeframe):
        """Standardize candle data format"""
        standardized_candles = []
        
        for candle in candles:
            try:
                standardized_candle = {
                    'timestamp': self._parse_timestamp(candle.get('timestamp')),
                    'open': float(candle.get('open', 0)),
                    'high': float(candle.get('high', 0)),
                    'low': float(candle.get('low', 0)),
                    'close': float(candle.get('close', 0)),
                    'volume': float(candle.get('volume', 0)),
                    'timeframe': timeframe
                }
                
                # Validate candle data
                if self._is_valid_candle(standardized_candle):
                    standardized_candles.append(standardized_candle)
                    
            except Exception as e:
                logging.warning(f"⚠️ Candle standardization error: {e}")
                continue
                
        return standardized_candles
        
    def _parse_timestamp(self, timestamp):
        """Parse timestamp from various formats"""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return datetime.utcnow()
        else:
            return datetime.utcnow()
            
    def _is_valid_candle(self, candle):
        """Validate candle data"""
        try:
            # Check for basic validity
            if (candle['open'] <= 0 or candle['high'] <= 0 or 
                candle['low'] <= 0 or candle['close'] <= 0):
                return False
                
            # Check high/low consistency
            if candle['high'] < candle['low']:
                return False
                
            # Check if high is highest and low is lowest
            if (candle['high'] < max(candle['open'], candle['close']) or
                candle['low'] > min(candle['open'], candle['close'])):
                return False
                
            return True
            
        except:
            return False
            
    async def calculate_technical_indicators(self, ohlcv_data):
        """Calculate basic technical indicators"""
        indicators_data = {}
        
        for pair, pair_data in ohlcv_data.items():
            try:
                indicators = {}
                
                for timeframe, candles in pair_data.get('ohlcv', {}).items():
                    if len(candles) >= 20:  # Minimum data for indicators
                        df = pd.DataFrame(candles)
                        timeframe_indicators = self._calculate_timeframe_indicators(df)
                        indicators[timeframe] = timeframe_indicators
                        
                indicators_data[pair] = indicators
                
            except Exception as e:
                logging.error(f"❌ Technical indicators error for {pair}: {e}")
                continue
                
        return indicators_data
        
    def _calculate_timeframe_indicators(self, df):
        """Calculate indicators for a single timeframe"""
        indicators = {}
        
        try:
            prices = df['close'].values
            highs = df['high'].values
            lows = df['low'].values
            volumes = df['volume'].values
            
            # Simple Moving Averages
            if len(prices) >= 20:
                indicators['sma_20'] = np.mean(prices[-20:])
            if len(prices) >= 50:
                indicators['sma_50'] = np.mean(prices[-50:])
                
            # RSI
            if len(prices) >= 14:
                indicators['rsi'] = self._calculate_rsi(prices)
                
            # Volume indicators
            if len(volumes) >= 20:
                indicators['volume_sma'] = np.mean(volumes[-20:])
                indicators['volume_trend'] = 'increasing' if volumes[-1] > indicators['volume_sma'] else 'decreasing'
                
            # Price range
            indicators['current_range'] = (highs[-1] - lows[-1]) / prices[-1]  # Normalized range
            
            return indicators
            
        except Exception as e:
            logging.error(f"❌ Timeframe indicators calculation error: {e}")
            return {}
            
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        try:
            if len(prices) < period + 1:
                return 50
                
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gains = np.mean(gains[-period:])
            avg_losses = np.mean(losses[-period:])
            
            if avg_losses == 0:
                return 100
                
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except:
            return 50
            
    async def detect_anomalies(self, ohlcv_data):
        """Detect data anomalies"""
        anomalies = {}
        
        for pair, pair_data in ohlcv_data.items():
            pair_anomalies = []
            
            for timeframe, candles in pair_data.get('ohlcv', {}).items():
                if len(candles) >= 10:
                    timeframe_anomalies = self._detect_timeframe_anomalies(candles, timeframe)
                    pair_anomalies.extend(timeframe_anomalies)
                    
            if pair_anomalies:
                anomalies[pair] = pair_anomalies
                
        return anomalies
        
    def _detect_timeframe_anomalies(self, candles, timeframe):
        """Detect anomalies in timeframe data"""
        anomalies = []
        
        try:
            prices = [c['close'] for c in candles]
            volumes = [c['volume'] for c in candles]
            
            # Price spike detection
            price_changes = np.abs(np.diff(prices) / prices[:-1])
            avg_change = np.mean(price_changes)
            std_change = np.std(price_changes)
            
            for i in range(1, len(price_changes)):
                if price_changes[i] > avg_change + 3 * std_change:
                    anomalies.append({
                        'type': 'price_spike',
                        'timeframe': timeframe,
                        'timestamp': candles[i+1]['timestamp'],
                        'severity': 'high'
                    })
                    
            # Volume spike detection
            avg_volume = np.mean(volumes)
            std_volume = np.std(volumes)
            
            for i, volume in enumerate(volumes):
                if volume > avg_volume + 3 * std_volume:
                    anomalies.append({
                        'type': 'volume_spike',
                        'timeframe': timeframe,
                        'timestamp': candles[i]['timestamp'],
                        'severity': 'medium'
                    })
                    
            # Missing data detection
            if len(candles) >= 2:
                time_diffs = []
                for i in range(1, len(candles)):
                    diff = (candles[i]['timestamp'] - candles[i-1]['timestamp']).total_seconds()
                    time_diffs.append(diff)
                    
                avg_diff = np.mean(time_diffs)
                for i, diff in enumerate(time_diffs):
                    if diff > avg_diff * 2:  # Gap larger than expected
                        anomalies.append({
                            'type': 'data_gap',
                            'timeframe': timeframe,
                            'timestamp': candles[i]['timestamp'],
                            'severity': 'low'
                        })
                        
        except Exception as e:
            logging.error(f"❌ Anomaly detection error: {e}")
            
        return anomalies
        
    async def cleanup(self):
        """Cleanup market data"""
        self.data_cache.clear()
        logging.info("🔒 Market data cleanup completed")
