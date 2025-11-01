"""
MULTI TIMEFRAME SYNCHRONIZER - Sinkronisasi analisis 1m–1D
"""

import logging
from datetime import datetime, timedelta
from config.settings import settings  # PASTIKAN IMPORT INI BENAR

class MultiTimeframeSynchronizer:
    def __init__(self):
        self.timeframes = settings.ENABLED_TIMEFRAMES  # SEKARANG SUDAH ADA
        
    async def initialize(self):
        """Initialize multi-timeframe synchronizer"""
        logging.info("⏰ INITIALIZING MULTI-TF SYNCHRONIZER...")
        
    async def synchronize(self, market_data):
        """Sinkronisasi data across timeframes"""
        synchronized_data = {}
        
        for pair in market_data.keys():
            try:
                pair_data = market_data[pair]
                synchronized_data[pair] = await self._synchronize_pair(pair_data)
            except Exception as e:
                logging.error(f"❌ TF sync error for {pair}: {e}")
                continue
                
        return synchronized_data
        
    # ... rest of the code remains the same ...        
    async def _synchronize_pair(self, pair_data):
        """Sinkronisasi data untuk satu pair"""
        tf_data = {}
        
        for tf in self.timeframes:
            try:
                # Filter data untuk timeframe tertentu
                tf_specific_data = self._resample_data(pair_data, tf)
                tf_data[tf] = tf_specific_data
            except Exception as e:
                logging.error(f"❌ TF {tf} resampling error: {e}")
                continue
                
        return tf_data
        
    def _resample_data(self, data, target_tf):
        """Resample data ke target timeframe"""
        if not data:
            return []
            
        # Simplified resampling - dalam implementasi nyata akan lebih kompleks
        resampled = []
        
        # Group data berdasarkan timeframe target
        tf_minutes = self._timeframe_to_minutes(target_tf)
        current_group = []
        
        for i, candle in enumerate(data):
            current_group.append(candle)
            
            # Jika sudah cukup data untuk timeframe target
            if len(current_group) >= tf_minutes:
                resampled_candle = self._create_resampled_candle(current_group, target_tf)
                resampled.append(resampled_candle)
                current_group = []
                
        return resampled
        
    def _timeframe_to_minutes(self, tf):
        """Convert timeframe string ke menit"""
        tf_map = {
            '1m': 1,
            '5m': 5, 
            '15m': 15,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }
        return tf_map.get(tf, 1)
        
    def _create_resampled_candle(self, group, tf):
        """Buat candle dari data yang di-resample"""
        opens = [c['open'] for c in group]
        highs = [c['high'] for c in group] 
        lows = [c['low'] for c in group]
        closes = [c['close'] for c in group]
        volumes = [c.get('volume', 0) for c in group]
        
        return {
            'open': opens[0],
            'high': max(highs),
            'low': min(lows),
            'close': closes[-1],
            'volume': sum(volumes),
            'timestamp': group[-1]['timestamp'],
            'timeframe': tf
        }
        
    def get_aligned_signals(self, analysis):
        """Dapatkan sinyal yang aligned across timeframes"""
        aligned = {}
        
        for pair, pair_analysis in analysis.items():
            # Check untuk konfirmasi multi timeframe
            tf_confirmations = self._check_tf_alignment(pair_analysis)
            aligned[pair] = tf_confirmations
            
        return aligned
        
    def _check_tf_alignment(self, pair_analysis):
        """Check alignment sinyal across timeframes"""
        confirmations = {
            'aligned': False,
            'confirming_tfs': [],
            'opposing_tfs': [],
            'alignment_score': 0.0
        }
        
        # Simplified alignment check
        bullish_tfs = []
        bearish_tfs = []
        
        for tf, analysis in pair_analysis.items():
            trend = analysis.get('trend_direction', 'neutral')
            
            if trend == 'bullish':
                bullish_tfs.append(tf)
            elif trend == 'bearish':
                bearish_tfs.append(tf)
                
        total_tfs = len(pair_analysis)
        if total_tfs == 0:
            return confirmations
            
        bullish_ratio = len(bullish_tfs) / total_tfs
        bearish_ratio = len(bearish_tfs) / total_tfs
        
        if bullish_ratio >= 0.6:
            confirmations['aligned'] = True
            confirmations['confirming_tfs'] = bullish_tfs
            confirmations['opposing_tfs'] = bearish_tfs
            confirmations['alignment_score'] = bullish_ratio
        elif bearish_ratio >= 0.6:
            confirmations['aligned'] = True
            confirmations['confirming_tfs'] = bearish_tfs
            confirmations['opposing_tfs'] = bullish_tfs
            confirmations['alignment_score'] = bearish_ratio
            
        return confirmations
