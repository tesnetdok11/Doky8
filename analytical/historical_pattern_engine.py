"""
HISTORICAL PATTERN ENGINE - Analisa pola histories
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class HistoricalPatternEngine:
    def __init__(self):
        self.pattern_database = "learning_memory/historical_patterns.json"
        self.historical_data = {}
        
    async def initialize(self):
        """Initialize historical pattern engine"""
        logging.info("📚 INITIALIZING HISTORICAL PATTERN ENGINE...")
        await self._load_historical_patterns()
        
    async def analyze(self, market_data, current_analysis):
        """Analisis pola historis"""
        pattern_analysis = {}
        
        for pair, data in market_data.items():
            try:
                analysis = await self._analyze_pair_history(pair, data, current_analysis.get(pair, {}))
                pattern_analysis[pair] = analysis
            except Exception as e:
                logging.error(f"❌ Historical pattern analysis error for {pair}: {e}")
                continue
                
        return pattern_analysis
        
    async def _analyze_pair_history(self, pair, current_data, current_analysis):
        """Analisis pola historis untuk satu pair"""
        analysis = {
            'similar_patterns': [],
            'historical_accuracy': 0.0,
            'seasonal_tendencies': [],
            'recurring_patterns': [],
            'volume_anomalies': [],
            'time_based_patterns': [],
            'pattern_confidence': 0.0
        }
        
        if len(current_data) < 100:
            return analysis
            
        # 1. Find Similar Historical Patterns
        analysis['similar_patterns'] = await self._find_similar_patterns(pair, current_data)
        
        # 2. Historical Accuracy
        analysis['historical_accuracy'] = self._calculate_historical_accuracy(analysis['similar_patterns'])
        
        # 3. Seasonal Tendencies
        analysis['seasonal_tendencies'] = self._analyze_seasonal_tendencies(pair, current_data)
        
        # 4. Recurring Patterns
        analysis['recurring_patterns'] = self._find_recurring_patterns(pair, current_data)
        
        # 5. Volume Anomalies
        analysis['volume_anomalies'] = self._detect_volume_anomalies(current_data)
        
        # 6. Time-based Patterns
        analysis['time_based_patterns'] = self._analyze_time_patterns(current_data)
        
        # 7. Pattern Confidence
        analysis['pattern_confidence'] = self._calculate_pattern_confidence(analysis)
        
        return analysis
        
    async def _find_similar_patterns(self, pair, current_data):
        """Temukan pola serupa dalam data historis"""
        similar_patterns = []
        current_df = pd.DataFrame(current_data)
        
        # Extract current pattern features
        current_features = self._extract_pattern_features(current_df)
        
        # Load historical patterns for this pair
        pair_history = self.historical_data.get(pair, [])
        
        for historical_pattern in pair_history[-100:]:  # Check recent 100 patterns
            similarity = self._calculate_pattern_similarity(current_features, historical_pattern['features'])
            
            if similarity > 0.7:  # 70% similarity threshold
                similar_patterns.append({
                    'pattern_id': historical_pattern['id'],
                    'similarity_score': similarity,
                    'historical_outcome': historical_pattern['outcome'],
                    'timestamp': historical_pattern['timestamp']
                })
                
        return sorted(similar_patterns, key=lambda x: x['similarity_score'], reverse=True)[:5]  # Top 5
        
    def _extract_pattern_features(self, df):
        """Ekstrak fitur pola dari data"""
        features = {}
        
        if len(df) < 20:
            return features
            
        prices = df['close'].values
        
        # Price movement features
        features['price_trend'] = (prices[-1] - prices[0]) / prices[0]
        features['volatility'] = np.std(prices) / np.mean(prices)
        
        # Volume features
        if 'volume' in df.columns:
            features['volume_trend'] = (df['volume'].iloc[-1] - df['volume'].iloc[0]) / df['volume'].iloc[0]
            features['volume_std'] = df['volume'].std()
            
        # Technical features
        features['rsi'] = self._calculate_rsi(prices)
        features['momentum'] = (prices[-1] - prices[-10]) / prices[-10] if len(prices) >= 10 else 0
        
        # Pattern-specific features
        features['swing_highs'] = self._count_swing_highs(df)
        features['swing_lows'] = self._count_swing_lows(df)
        
        return features
        
    def _calculate_rsi(self, prices, period=14):
        """Hitung RSI"""
        if len(prices) < period + 1:
            return 50
            
        gains = np.where(np.diff(prices) > 0, np.diff(prices), 0)
        losses = np.where(np.diff(prices) < 0, -np.diff(prices), 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        else:
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
            
    def _count_swing_highs(self, df):
        """Hitung jumlah swing highs"""
        highs = df['high'].values
        count = 0
        
        for i in range(2, len(highs)-2):
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                count += 1
                
        return count
        
    def _count_swing_lows(self, df):
        """Hitung jumlah swing lows"""
        lows = df['low'].values
        count = 0
        
        for i in range(2, len(lows)-2):
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                count += 1
                
        return count
        
    def _calculate_pattern_similarity(self, features1, features2):
        """Hitung similarity antara dua set fitur"""
        if not features1 or not features2:
            return 0.0
            
        common_features = set(features1.keys()) & set(features2.keys())
        if not common_features:
            return 0.0
            
        similarities = []
        for feature in common_features:
            val1 = features1[feature]
            val2 = features2[feature]
            
            # Normalize similarity calculation based on feature type
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                max_val = max(abs(val1), abs(val2), 1)  # Avoid division by zero
                similarity = 1 - (abs(val1 - val2) / max_val)
                similarities.append(max(0, similarity))
                
        return np.mean(similarities) if similarities else 0.0
        
    def _calculate_historical_accuracy(self, similar_patterns):
        """Hitung akurasi historis berdasarkan pola serupa"""
        if not similar_patterns:
            return 0.5  # Default confidence
            
        successful_patterns = len([p for p in similar_patterns if p['historical_outcome'] == 'success'])
        total_patterns = len(similar_patterns)
        
        return successful_patterns / total_patterns if total_patterns > 0 else 0.5
        
    def _analyze_seasonal_tendencies(self, pair, current_data):
        """Analisis kecenderungan musiman"""
        tendencies = []
        current_time = datetime.utcnow()
        
        # Day of week patterns
        day_of_week = current_time.weekday()
        day_patterns = {
            0: "monday_volatility",  # Monday
            4: "friday_breakouts"    # Friday
        }
        
        if day_of_week in day_patterns:
            tendencies.append({
                'type': 'day_of_week',
                'pattern': day_patterns[day_of_week],
                'strength': 'medium'
            })
            
        # Time of day patterns (market sessions)
        current_hour = current_time.hour
        
        session_patterns = {
            (0, 8): "asian_session_range",
            (7, 16): "london_session_volatility", 
            (13, 22): "newyork_session_trends"
        }
        
        for (start, end), pattern in session_patterns.items():
            if start <= current_hour < end:
                tendencies.append({
                    'type': 'market_session',
                    'pattern': pattern,
                    'strength': 'medium'
                })
                
        return tendencies
        
    def _find_recurring_patterns(self, pair, current_data):
        """Temukan pola yang berulang"""
        recurring = []
        current_df = pd.DataFrame(current_data)
        
        # Check for common chart patterns
        patterns_to_check = [
            self._detect_head_shoulders,
            self._detect_double_top_bottom,
            self._detect_triangle_patterns
        ]
        
        for pattern_detector in patterns_to_check:
            detected = pattern_detector(current_df)
            if detected:
                recurring.append(detected)
                
        return recurring
        
    def _detect_head_shoulders(self, df):
        """Deteksi pola head and shoulders"""
        if len(df) < 30:
            return None
            
        highs = df['high'].values
        
        # Simplified H&S detection
        for i in range(15, len(highs)-15):
            left_shoulder = max(highs[i-10:i-5])
            head = max(highs[i-5:i+5])
            right_shoulder = max(highs[i+5:i+10])
            
            neckline = (min(highs[i-10:i-5]) + min(highs[i+5:i+10])) / 2
            
            if (left_shoulder < head and right_shoulder < head and
                abs(left_shoulder - right_shoulder) / left_shoulder < 0.05):
                return {
                    'type': 'head_shoulders',
                    'direction': 'bearish',
                    'confidence': 'medium',
                    'neckline': neckline
                }
                
        return None
        
    def _detect_double_top_bottom(self, df):
        """Deteksi pola double top/bottom"""
        if len(df) < 20:
            return None
            
        highs = df['high'].values
        lows = df['low'].values
        
        # Double Top
        for i in range(10, len(highs)-10):
            if (abs(highs[i] - highs[i-5]) / highs[i] < 0.02 and  # Similar highs
                lows[i] < lows[i-5]):  # Lower low between
                return {
                    'type': 'double_top',
                    'direction': 'bearish',
                    'confidence': 'medium'
                }
                
        # Double Bottom
        for i in range(10, len(lows)-10):
            if (abs(lows[i] - lows[i-5]) / lows[i] < 0.02 and  # Similar lows
                highs[i] > highs[i-5]):  # Higher high between
                return {
                    'type': 'double_bottom',
                    'direction': 'bullish', 
                    'confidence': 'medium'
                }
                
        return None
        
    def _detect_triangle_patterns(self, df):
        """Deteksi pola triangle"""
        if len(df) < 20:
            return None
            
        highs = df['high'].values
        lows = df['low'].values
        
        # Check for converging highs and lows
        early_highs = np.std(highs[:10])
        late_highs = np.std(highs[-10:])
        early_lows = np.std(lows[:10])
        late_lows = np.std(lows[-10:])
        
        if (late_highs < early_highs * 0.7 and
            late_lows < early_lows * 0.7):
            return {
                'type': 'triangle',
                'direction': 'neutral',
                'confidence': 'medium'
            }
            
        return None
        
    def _detect_volume_anomalies(self, current_data):
        """Deteksi anomali volume"""
        anomalies = []
        df = pd.DataFrame(current_data)
        
        if 'volume' not in df.columns:
            return anomalies
            
        avg_volume = df['volume'].mean()
        std_volume = df['volume'].std()
        
        for i in range(len(df)):
            volume = df.iloc[i]['volume']
            if volume > avg_volume + 2 * std_volume:
                anomalies.append({
                    'type': 'volume_spike',
                    'magnitude': (volume - avg_volume) / std_volume,
                    'timestamp': df.iloc[i]['timestamp']
                })
                
        return anomalies
        
    def _analyze_time_patterns(self, current_data):
        """Analisis pola berdasarkan waktu"""
        time_patterns = []
        df = pd.DataFrame(current_data)
        
        # Analyze intraday patterns
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            
            # Check for specific hour patterns
            hour_volatility = df.groupby('hour')['close'].std()
            volatile_hours = hour_volatility[hour_volatility > hour_volatility.median()]
            
            for hour in volatile_hours.index:
                time_patterns.append({
                    'type': 'high_volatility_hour',
                    'hour': hour,
                    'strength': 'medium'
                })
                
        return time_patterns
        
    def _calculate_pattern_confidence(self, analysis):
        """Hitung confidence berdasarkan analisis pola"""
        weights = {
            'historical_accuracy': 0.4,
            'similar_patterns_count': 0.3,
            'recurring_patterns': 0.2,
            'seasonal_tendencies': 0.1
        }
        
        score = 0.0
        
        # Historical accuracy
        score += analysis['historical_accuracy'] * weights['historical_accuracy']
        
        # Similar patterns count
        similar_count = len(analysis['similar_patterns'])
        score += min(similar_count / 5, 1.0) * weights['similar_patterns_count']
        
        # Recurring patterns
        if analysis['recurring_patterns']:
            score += weights['recurring_patterns']
            
        # Seasonal tendencies
        if analysis['seasonal_tendencies']:
            score += weights['seasonal_tendencies']
            
        return min(score, 1.0)
        
    async def _load_historical_patterns(self):
        """Load pola historis dari database"""
        try:
            import os
            if os.path.exists(self.pattern_database):
                with open(self.pattern_database, 'r') as f:
                    self.historical_data = json.load(f)
            else:
                self.historical_data = {}
                logging.info("📝 No historical pattern database found")
        except Exception as e:
            logging.error(f"❌ Error loading historical patterns: {e}")
            self.historical_data = {}
            
    async def update_pattern_database(self, pair, pattern_features, outcome):
        """Update database pola dengan hasil baru"""
        try:
            pattern_id = f"{pair}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            new_pattern = {
                'id': pattern_id,
                'pair': pair,
                'features': pattern_features,
                'outcome': outcome,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if pair not in self.historical_data:
                self.historical_data[pair] = []
                
            self.historical_data[pair].append(new_pattern)
            
            # Keep only recent patterns
            if len(self.historical_data[pair]) > 1000:
                self.historical_data[pair] = self.historical_data[pair][-1000:]
                
            # Save to file
            with open(self.pattern_database, 'w') as f:
                json.dump(self.historical_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"❌ Error updating pattern database: {e}")
