"""
AGGR DATA LOADER - Integrasi data aggregated trades dari Tucsky/aggr
"""

import logging
import aiohttp
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
import json
from pathlib import Path
from config.settings import settings  # TAMBAHKAN IMPORT INI

class AggrDataLoader:
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/Tucsky/aggr/main/data"
        self.cache_dir = "data/aggr_cache"
        self.session = None
        self.cache_duration = 3600  # 1 hour cache
        
    async def initialize(self):
        """Initialize Aggr data loader"""
        logging.info("📊 INITIALIZING TUCSKY AGGR DATA LOADER...")
        
        # Create cache directory
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Create aiohttp session dengan timeout dari settings
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Test connection
        if await self._test_connection():
            logging.info("✅ TUCSKY AGGR DATA LOADER CONNECTED")
        else:
            logging.error("❌ TUCSKY AGGR DATA LOADER CONNECTION FAILED")
            
    # ... rest of the code ...            
    async def _test_connection(self):
        """Test connection to Tucsky aggr data"""
        try:
            test_url = f"{self.base_url}/BTCUSDT/2024/01/BTCUSDT-2024-01-01-aggr.csv"
            async with self.session.head(test_url) as response:
                return response.status in [200, 404]  # 404 is ok for test
        except Exception as e:
            logging.error(f"❌ Aggr connection test failed: {e}")
            return False
            
    async def fetch_aggr_data(self, pair, date=None):
        """Fetch aggregated trade data for specific pair and date"""
        if date is None:
            date = datetime.utcnow()
            
        try:
            # Convert pair to Tucsky format (e.g., BTCUSDT -> BTCUSDT)
            tucsky_pair = pair.replace("-", "").replace("/", "")
            
            # Build URL path
            year = date.strftime("%Y")
            month = date.strftime("%m")
            day = date.strftime("%d")
            
            filename = f"{tucsky_pair}-{year}-{month}-{day}-aggr.csv"
            url = f"{self.base_url}/{tucsky_pair}/{year}/{month}/{filename}"
            
            # Check cache first
            cache_file = f"{self.cache_dir}/{filename}"
            cached_data = await self._load_from_cache(cache_file)
            if cached_data is not None:
                logging.debug(f"📁 Using cached aggr data for {pair}")
                return cached_data
                
            # Fetch from GitHub
            logging.info(f"🌐 Fetching aggr data for {pair} - {date.strftime('%Y-%m-%d')}")
            async with self.session.get(url) as response:
                if response.status == 200:
                    csv_content = await response.text()
                    parsed_data = await self._parse_aggr_csv(csv_content, pair)
                    
                    # Cache the data
                    await self._save_to_cache(cache_file, parsed_data)
                    
                    return parsed_data
                else:
                    logging.warning(f"⚠️ No aggr data found for {pair} on {date.strftime('%Y-%m-%d')}")
                    return None
                    
        except Exception as e:
            logging.error(f"❌ Aggr data fetch error for {pair}: {e}")
            return None
            
    async def _parse_aggr_csv(self, csv_content, pair):
        """Parse Tucsky aggr CSV format"""
        try:
            # Parse CSV into DataFrame
            df = pd.read_csv(pd.compat.StringIO(csv_content))
            
            # Standardize column names
            df.columns = [col.strip().lower() for col in df.columns]
            
            # Convert timestamp to datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            elif 'date' in df.columns:
                df['timestamp'] = pd.to_datetime(df['date'])
                
            # Ensure required columns
            required_columns = ['timestamp', 'price', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    logging.error(f"❌ Missing required column {col} in aggr data")
                    return None
                    
            # Add pair information
            df['pair'] = pair
            
            # Calculate additional metrics
            df = await self._calculate_aggr_metrics(df)
            
            return {
                'pair': pair,
                'data': df.to_dict('records'),
                'summary': await self._generate_aggr_summary(df),
                'timestamp': datetime.utcnow(),
                'data_points': len(df)
            }
            
        except Exception as e:
            logging.error(f"❌ Aggr CSV parsing error: {e}")
            return None
            
    async def _calculate_aggr_metrics(self, df):
        """Calculate additional metrics from aggregated data"""
        try:
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Price movement
            df['price_change'] = df['price'].pct_change()
            df['price_change_abs'] = df['price'].diff()
            
            # Volume analysis
            df['volume_ma'] = df['volume'].rolling(window=20, min_periods=1).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma']
            
            # Trade intensity
            df['trade_intensity'] = df['volume'] * abs(df['price_change'])
            
            # Buy/Sell pressure (if side information available)
            if 'side' in df.columns:
                df['buy_volume'] = df[df['side'] == 'buy']['volume']
                df['sell_volume'] = df[df['side'] == 'sell']['volume']
                df['buy_sell_ratio'] = df['buy_volume'] / (df['sell_volume'] + 0.0001)
            else:
                # Estimate buy/sell based on price movement
                df['estimated_side'] = np.where(df['price_change'] > 0, 'buy', 'sell')
                
            return df
            
        except Exception as e:
            logging.error(f"❌ Aggr metrics calculation error: {e}")
            return df
            
    async def _generate_aggr_summary(self, df):
        """Generate summary statistics from aggregated data"""
        try:
            if df.empty:
                return {}
                
            summary = {
                'total_volume': df['volume'].sum(),
                'total_trades': len(df),
                'avg_trade_size': df['volume'].mean(),
                'price_range': {
                    'high': df['price'].max(),
                    'low': df['price'].min(),
                    'avg': df['price'].mean()
                },
                'volume_profile': {
                    'peak_volume': df['volume'].max(),
                    'avg_volume': df['volume'].mean(),
                    'volume_std': df['volume'].std()
                },
                'time_period': {
                    'start': df['timestamp'].min().isoformat(),
                    'end': df['timestamp'].max().isoformat(),
                    'duration_hours': (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
                }
            }
            
            # Add volatility metrics
            if 'price_change' in df.columns:
                summary['volatility'] = {
                    'price_change_std': df['price_change'].std(),
                    'max_price_change': df['price_change'].max(),
                    'min_price_change': df['price_change'].min()
                }
                
            return summary
            
        except Exception as e:
            logging.error(f"❌ Aggr summary generation error: {e}")
            return {}
            
    async def _load_from_cache(self, cache_file):
        """Load data from cache if fresh"""
        try:
            if not Path(cache_file).exists():
                return None
                
            # Check cache age
            file_age = datetime.utcnow().timestamp() - Path(cache_file).stat().st_mtime
            if file_age > self.cache_duration:
                return None
                
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                
            return cached_data
            
        except Exception as e:
            logging.error(f"❌ Cache load error: {e}")
            return None
            
    async def _save_to_cache(self, cache_file, data):
        """Save data to cache"""
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"❌ Cache save error: {e}")
            
    async def get_recent_aggr_data(self, pair, days_back=7):
        """Get aggregated data for recent days"""
        try:
            all_data = []
            
            for i in range(days_back):
                date = datetime.utcnow() - timedelta(days=i)
                daily_data = await self.fetch_aggr_data(pair, date)
                
                if daily_data and daily_data['data']:
                    all_data.extend(daily_data['data'])
                    
            if all_data:
                df = pd.DataFrame(all_data)
                return {
                    'pair': pair,
                    'data': df.to_dict('records'),
                    'summary': await self._generate_aggr_summary(df),
                    'total_days': days_back,
                    'total_trades': len(all_data)
                }
            else:
                return None
                
        except Exception as e:
            logging.error(f"❌ Recent aggr data error for {pair}: {e}")
            return None
            
    async def analyze_market_depth(self, aggr_data):
        """Analyze market depth from aggregated data"""
        try:
            if not aggr_data or not aggr_data['data']:
                return {}
                
            df = pd.DataFrame(aggr_data['data'])
            
            # Group by price levels to simulate order book
            price_precision = self._get_price_precision(df['price'].mean())
            df['price_level'] = (df['price'] / price_precision).round() * price_precision
            
            depth_data = df.groupby('price_level').agg({
                'volume': 'sum',
                'trade_intensity': 'mean',
                'timestamp': 'count'  # Number of trades at this level
            }).reset_index()
            
            depth_data = depth_data.rename(columns={'timestamp': 'trade_count'})
            depth_data = depth_data.sort_values('price_level')
            
            # Separate bids and asks (simplified)
            current_price = df['price'].iloc[-1]
            depth_data['side'] = np.where(
                depth_data['price_level'] < current_price, 'bid', 'ask'
            )
            
            return {
                'current_price': current_price,
                'depth_levels': depth_data.to_dict('records'),
                'bid_ask_spread': await self._calculate_bid_ask_spread(depth_data, current_price),
                'support_resistance_levels': await self._find_support_resistance(depth_data)
            }
            
        except Exception as e:
            logging.error(f"❌ Market depth analysis error: {e}")
            return {}
            
    def _get_price_precision(self, price):
        """Determine appropriate price precision for grouping"""
        if price > 1000:
            return 1.0
        elif price > 100:
            return 0.1
        elif price > 10:
            return 0.01
        elif price > 1:
            return 0.001
        else:
            return 0.0001
            
    async def _calculate_bid_ask_spread(self, depth_data, current_price):
        """Calculate bid-ask spread from depth data"""
        try:
            bids = [d for d in depth_data if d['side'] == 'bid']
            asks = [d for d in depth_data if d['side'] == 'ask']
            
            if not bids or not asks:
                return {}
                
            best_bid = max(b['price_level'] for b in bids)
            best_ask = min(a['price_level'] for a in asks)
            
            spread = best_ask - best_bid
            spread_percent = (spread / current_price) * 100
            
            return {
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread_absolute': spread,
                'spread_percent': spread_percent,
                'spread_level': 'tight' if spread_percent < 0.1 else 'wide'
            }
            
        except Exception as e:
            logging.error(f"❌ Spread calculation error: {e}")
            return {}
            
    async def _find_support_resistance(self, depth_data):
        """Find support and resistance levels from depth data"""
        try:
            # Find price levels with high volume (potential S/R)
            high_volume_levels = depth_data.nlargest(10, 'volume')
            
            support_levels = []
            resistance_levels = []
            current_price = depth_data['price_level'].mean()  # Approximate
            
            for level in high_volume_levels.to_dict('records'):
                if level['price_level'] < current_price:
                    support_levels.append(level)
                else:
                    resistance_levels.append(level)
                    
            return {
                'support_levels': sorted(support_levels, key=lambda x: x['price_level'], reverse=True)[:5],
                'resistance_levels': sorted(resistance_levels, key=lambda x: x['price_level'])[:5]
            }
            
        except Exception as e:
            logging.error(f"❌ Support/resistance analysis error: {e}")
            return {}
            
    async def detect_large_orders(self, aggr_data, threshold_ratio=5):
        """Detect large orders in aggregated data"""
        try:
            if not aggr_data or not aggr_data['data']:
                return []
                
            df = pd.DataFrame(aggr_data['data'])
            avg_trade_size = df['volume'].mean()
            large_orders_threshold = avg_trade_size * threshold_ratio
            
            large_orders = df[df['volume'] > large_orders_threshold].copy()
            large_orders = large_orders.sort_values('volume', ascending=False)
            
            detected_orders = []
            for _, order in large_orders.iterrows():
                detected_orders.append({
                    'timestamp': order['timestamp'],
                    'price': order['price'],
                    'volume': order['volume'],
                    'size_ratio': order['volume'] / avg_trade_size,
                    'estimated_side': order.get('estimated_side', 'unknown'),
                    'significance': 'high' if order['volume'] > avg_trade_size * 10 else 'medium'
                })
                
            return detected_orders
            
        except Exception as e:
            logging.error(f"❌ Large order detection error: {e}")
            return []
            
    async def cleanup(self):
        """Cleanup Aggr data loader"""
        if self.session:
            await self.session.close()
            
        # Clean old cache files
        await self._cleanup_old_cache()
        
        logging.info("🔒 Aggr data loader cleanup completed")
        
    async def _cleanup_old_cache(self):
        """Cleanup old cache files"""
        try:
            cache_dir = Path(self.cache_dir)
            cutoff_time = datetime.utcnow().timestamp() - (self.cache_duration * 2)
            
            for cache_file in cache_dir.glob("*.json"):
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    
        except Exception as e:
            logging.error(f"❌ Cache cleanup error: {e}")
