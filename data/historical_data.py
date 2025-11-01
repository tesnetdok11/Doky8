"""
HISTORICAL DATA - Database harga masa lalu
"""

import logging
import sqlite3
import pandas as pd
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from config.pairs import TOP_25_PAIRS

class HistoricalData:
    def __init__(self):
        self.db_path = "data/historical/crypto_data.db"
        self.connection = None
        
    async def initialize(self):
        """Initialize historical database"""
        logging.info("🗃️ INITIALIZING HISTORICAL DATABASE...")
        
        try:
            # Create data directory
            Path("data/historical").mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            await self._create_tables()
            
            logging.info("✅ HISTORICAL DATABASE INITIALIZED")
            
        except Exception as e:
            logging.error(f"❌ Historical database initialization failed: {e}")
            
    async def _create_tables(self):
        """Create database tables"""
        try:
            cursor = self.connection.cursor()
            
            # OHLCV data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ohlcv_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    exchange TEXT DEFAULT 'binance',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(pair, timeframe, timestamp)
                )
            ''')
            
            # Market structure data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_structure (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    trend_direction TEXT,
                    trend_strength REAL,
                    key_levels TEXT,  -- JSON
                    liquidity_zones TEXT,  -- JSON
                    bos_confirmed BOOLEAN,
                    choch_confirmed BOOLEAN,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Pattern data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pattern_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    pattern_data TEXT,  -- JSON
                    strength TEXT,
                    direction TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Price action data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_action (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    candle_patterns TEXT,  -- JSON
                    momentum_indicators TEXT,  -- JSON
                    support_resistance TEXT,  -- JSON
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ohlcv_pair_time ON ohlcv_data(pair, timeframe, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_structure_pair_time ON market_structure(pair, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_pair_time ON pattern_data(pair, timestamp)')
            
            self.connection.commit()
            logging.info("✅ Database tables created successfully")
            
        except Exception as e:
            logging.error(f"❌ Table creation error: {e}")
            self.connection.rollback()
            
    async def store_ohlcv_data(self, ohlcv_data):
        """Store OHLCV data in database"""
        try:
            cursor = self.connection.cursor()
            stored_count = 0
            
            for pair, pair_data in ohlcv_data.items():
                ohlcv = pair_data.get('ohlcv', {})
                
                for timeframe, candles in ohlcv.items():
                    for candle in candles:
                        try:
                            cursor.execute('''
                                INSERT OR IGNORE INTO ohlcv_data 
                                (pair, timeframe, timestamp, open, high, low, close, volume, exchange)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                pair,
                                timeframe,
                                candle['timestamp'],
                                candle['open'],
                                candle['high'], 
                                candle['low'],
                                candle['close'],
                                candle['volume'],
                                pair_data.get('exchange', 'binance')
                            ))
                            stored_count += 1
                        except Exception as e:
                            logging.warning(f"⚠️ OHLCV storage error for {pair} {timeframe}: {e}")
                            continue
                            
            self.connection.commit()
            logging.info(f"💾 Stored {stored_count} OHLCV records")
            
        except Exception as e:
            logging.error(f"❌ OHLCV storage error: {e}")
            self.connection.rollback()
            
    async def store_market_structure(self, structure_analysis):
        """Store market structure analysis"""
        try:
            cursor = self.connection.cursor()
            stored_count = 0
            
            for pair, analysis in structure_analysis.items():
                cursor.execute('''
                    INSERT INTO market_structure 
                    (pair, timestamp, trend_direction, trend_strength, key_levels, liquidity_zones, bos_confirmed, choch_confirmed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pair,
                    datetime.utcnow(),
                    analysis.get('trend_direction'),
                    analysis.get('trend_strength'),
                    json.dumps(analysis.get('key_levels', [])),
                    json.dumps(analysis.get('liquidity_zones', [])),
                    analysis.get('bos_confirmed', False),
                    analysis.get('choch_confirmed', False)
                ))
                stored_count += 1
                
            self.connection.commit()
            logging.info(f"💾 Stored {stored_count} market structure records")
            
        except Exception as e:
            logging.error(f"❌ Market structure storage error: {e}")
            self.connection.rollback()
            
    async def store_patterns(self, pattern_analysis):
        """Store pattern analysis"""
        try:
            cursor = self.connection.cursor()
            stored_count = 0
            
            for pair, analysis in pattern_analysis.items():
                patterns = analysis.get('patterns', [])
                
                for pattern in patterns:
                    cursor.execute('''
                        INSERT INTO pattern_data 
                        (pair, pattern_type, timeframe, timestamp, pattern_data, strength, direction)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        pair,
                        pattern.get('type'),
                        pattern.get('timeframe', '15m'),
                        pattern.get('timestamp', datetime.utcnow()),
                        json.dumps(pattern),
                        pattern.get('strength', 'medium'),
                        pattern.get('direction', 'neutral')
                    ))
                    stored_count += 1
                    
            self.connection.commit()
            logging.info(f"💾 Stored {stored_count} pattern records")
            
        except Exception as e:
            logging.error(f"❌ Pattern storage error: {e}")
            self.connection.rollback()
            
    async def get_historical_ohlcv(self, pair, timeframe, start_date, end_date=None, limit=1000):
        """Get historical OHLCV data"""
        try:
            if end_date is None:
                end_date = datetime.utcnow()
                
            query = '''
                SELECT timestamp, open, high, low, close, volume 
                FROM ohlcv_data 
                WHERE pair = ? AND timeframe = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, self.connection, 
                                 params=[pair, timeframe, start_date, end_date, limit])
            
            return df
            
        except Exception as e:
            logging.error(f"❌ Historical OHLCV query error: {e}")
            return pd.DataFrame()
            
    async def get_market_structure_history(self, pair, hours_back=24):
        """Get market structure history"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            query = '''
                SELECT timestamp, trend_direction, trend_strength, key_levels, liquidity_zones, bos_confirmed, choch_confirmed
                FROM market_structure
                WHERE pair = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            '''
            
            cursor = self.connection.cursor()
            cursor.execute(query, (pair, start_time))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'timestamp': row[0],
                    'trend_direction': row[1],
                    'trend_strength': row[2],
                    'key_levels': json.loads(row[3]) if row[3] else [],
                    'liquidity_zones': json.loads(row[4]) if row[4] else [],
                    'bos_confirmed': bool(row[5]),
                    'choch_confirmed': bool(row[6])
                })
                
            return results
            
        except Exception as e:
            logging.error(f"❌ Market structure history error: {e}")
            return []
            
    async def get_pattern_frequency(self, pair, pattern_type, days_back=30):
        """Get pattern frequency statistics"""
        try:
            start_time = datetime.utcnow() - timedelta(days=days_back)
            
            query = '''
                SELECT COUNT(*) as count, strength, direction
                FROM pattern_data
                WHERE pair = ? AND pattern_type = ? AND timestamp >= ?
                GROUP BY strength, direction
            '''
            
            cursor = self.connection.cursor()
            cursor.execute(query, (pair, pattern_type, start_time))
            
            stats = {
                'total_count': 0,
                'by_strength': {},
                'by_direction': {}
            }
            
            for row in cursor.fetchall():
                count, strength, direction = row
                stats['total_count'] += count
                stats['by_strength'][strength] = stats['by_strength'].get(strength, 0) + count
                stats['by_direction'][direction] = stats['by_direction'].get(direction, 0) + count
                
            return stats
            
        except Exception as e:
            logging.error(f"❌ Pattern frequency error: {e}")
            return {}
            
    async def calculate_price_correlation(self, pair1, pair2, timeframe='1h', days_back=30):
        """Calculate price correlation between two pairs"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get data for both pairs
            data1 = await self.get_historical_ohlcv(pair1, timeframe, start_date)
            data2 = await self.get_historical_ohlcv(pair2, timeframe, start_date)
            
            if data1.empty or data2.empty:
                return 0.0
                
            # Merge on timestamp
            merged = pd.merge(data1, data2, on='timestamp', suffixes=('_1', '_2'))
            
            if merged.empty:
                return 0.0
                
            # Calculate correlation
            correlation = merged['close_1'].corr(merged['close_2'])
            return correlation if not pd.isna(correlation) else 0.0
            
        except Exception as e:
            logging.error(f"❌ Price correlation error: {e}")
            return 0.0
            
    async def get_volatility_history(self, pair, timeframe='1h', days_back=7):
        """Get volatility history"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            data = await self.get_historical_ohlcv(pair, timeframe, start_date)
            
            if data.empty:
                return []
                
            # Calculate daily volatility (standard deviation of returns)
            data['returns'] = data['close'].pct_change()
            data['volatility'] = data['returns'].rolling(window=24).std()  # 24 periods for daily vol
            
            # Group by date and get average volatility
            data['date'] = pd.to_datetime(data['timestamp']).dt.date
            daily_vol = data.groupby('date')['volatility'].mean().reset_index()
            
            return daily_vol.to_dict('records')
            
        except Exception as e:
            logging.error(f"❌ Volatility history error: {e}")
            return []
            
    async def cleanup_old_data(self, days_to_keep=90):
        """Cleanup data older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            cursor = self.connection.cursor()
            
            tables = ['ohlcv_data', 'market_structure', 'pattern_data', 'price_action']
            total_deleted = 0
            
            for table in tables:
                cursor.execute(f'DELETE FROM {table} WHERE timestamp < ?', (cutoff_date,))
                total_deleted += cursor.rowcount
                
            self.connection.commit()
            logging.info(f"🧹 Cleaned up {total_deleted} records older than {days_to_keep} days")
            
        except Exception as e:
            logging.error(f"❌ Data cleanup error: {e}")
            self.connection.rollback()
            
    async def get_database_stats(self):
        """Get database statistics"""
        try:
            cursor = self.connection.cursor()
            stats = {}
            
            tables = ['ohlcv_data', 'market_structure', 'pattern_data', 'price_action']
            
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[table] = cursor.fetchone()[0]
                
            # Get oldest and newest records
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM ohlcv_data')
            time_range = cursor.fetchone()
            stats['data_range'] = {
                'oldest': time_range[0],
                'newest': time_range[1]
            }
            
            return stats
            
        except Exception as e:
            logging.error(f"❌ Database stats error: {e}")
            return {}
            
    async def backup_database(self):
        """Create database backup"""
        try:
            backup_path = f"data/historical/backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Create backup connection
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            
            logging.info(f"💾 Database backed up to: {backup_path}")
            return backup_path
            
        except Exception as e:
            logging.error(f"❌ Database backup error: {e}")
            return None
            
    async def cleanup(self):
        """Cleanup historical data"""
        if self.connection:
            self.connection.close()
        logging.info("🔒 Historical data cleanup completed")
