"""
BINANCE API - Koneksi data real-time Binance
"""

import logging
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from config.settings import settings
from config.pairs import TOP_25_PAIRS

class BinanceAPI:
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.websocket_url = "wss://stream.binance.com:9443/ws"
        self.api_key = None  # Jangan langsung assign
        self.secret_key = None
        self.session = None
        self.websocket = None
    def _test_connection(self):
        """Test koneksi Binance - METHOD YANG DIBUTUHKAN"""
        try:
            if self.client:
                # Test dengan public endpoint
                self.client.get_server_time()
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Binance connection test failed: {e}")
            return False        
    
    async def initialize(self):
        """Initialize Binance API connection"""
        logging.info("🔗 INITIALIZING BINANCE API...")
        
        # Load API keys from environment - SEKARANG SUDAH ADA
        self.api_key = settings.BINANCE_API_KEY
        self.secret_key = settings.BINANCE_SECRET_KEY
        
        # Check if API keys are available
        if not self.api_key or not self.secret_key:
            logging.warning("⚠️ Binance API keys not configured - Using public endpoints only")
        
        # Create aiohttp session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.BINANCE_TIMEOUT)
        )
        
        # Test connection (public endpoints don't require API keys)
        if await self._test_connection():
            logging.info("✅ BINANCE API CONNECTED SUCCESSFULLY")
        else:
            logging.error("❌ BINANCE API CONNECTION FAILED")
            
    # ... rest of the methods remain the same ...
    async def _fetch_pair_data(self, pair):
        """Fetch data for single pair"""
        try:
            # Get current price and 24h stats
            ticker_url = f"{self.base_url}/api/v3/ticker/24hr?symbol={pair}"
            async with self.session.get(ticker_url) as response:
                if response.status == 200:
                    ticker_data = await response.json()
                    
            # Get OHLCV data for multiple timeframes - GUNAKAN settings.ENABLED_TIMEFRAMES
            ohlcv_data = {}
            for tf in settings.ENABLED_TIMEFRAMES:  # SEKARANG SUDAH ADA
                kline_data = await self._fetch_klines(pair, tf, limit=100)
                if kline_data:
                    ohlcv_data[tf] = kline_data
                    
            return {
                'pair': pair,
                'current_price': float(ticker_data['lastPrice']),
                'price_change_24h': float(ticker_data['priceChange']),
                'price_change_percent_24h': float(ticker_data['priceChangePercent']),
                'volume_24h': float(ticker_data['volume']),
                'high_24h': float(ticker_data['highPrice']),
                'low_24h': float(ticker_data['lowPrice']),
                'ohlcv': ohlcv_data,
                'timestamp': datetime.utcnow(),
                'exchange': 'binance'
            }
            
        except Exception as e:
            logging.error(f"❌ Pair data fetch error for {pair}: {e}")
            return None
            
    # ... rest of the code ...            
    async def fetch_market_data(self):
        """Fetch market data for all pairs"""
        market_data = {}
        
        try:
            tasks = []
            for pair in TOP_25_PAIRS:
                task = asyncio.create_task(self._fetch_pair_data(pair))
                tasks.append(task)
                
            # Fetch all pairs concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for pair, result in zip(TOP_25_PAIRS, results):
                if isinstance(result, Exception):
                    logging.error(f"❌ Error fetching {pair}: {result}")
                    continue
                if result:
                    market_data[pair] = result
                    
            logging.info(f"📊 Fetched data for {len(market_data)} pairs from Binance")
            return market_data
            
        except Exception as e:
            logging.error(f"❌ Market data fetch error: {e}")
            return {}
            
    async def _fetch_pair_data(self, pair):
        """Fetch data for single pair"""
        try:
            # Get current price and 24h stats
            ticker_url = f"{self.base_url}/api/v3/ticker/24hr?symbol={pair}"
            async with self.session.get(ticker_url) as response:
                if response.status == 200:
                    ticker_data = await response.json()
                    
            # Get OHLCV data for multiple timeframes
            ohlcv_data = {}
            for tf in settings.ENABLED_TIMEFRAMES:
                kline_data = await self._fetch_klines(pair, tf, limit=100)
                if kline_data:
                    ohlcv_data[tf] = kline_data
                    
            return {
                'pair': pair,
                'current_price': float(ticker_data['lastPrice']),
                'price_change_24h': float(ticker_data['priceChange']),
                'price_change_percent_24h': float(ticker_data['priceChangePercent']),
                'volume_24h': float(ticker_data['volume']),
                'high_24h': float(ticker_data['highPrice']),
                'low_24h': float(ticker_data['lowPrice']),
                'ohlcv': ohlcv_data,
                'timestamp': datetime.utcnow(),
                'exchange': 'binance'
            }
            
        except Exception as e:
            logging.error(f"❌ Pair data fetch error for {pair}: {e}")
            return None
            
    async def _fetch_klines(self, pair, timeframe, limit=100):
        """Fetch kline (OHLCV) data"""
        try:
            # Map timeframe to Binance interval
            tf_map = {
                '1m': '1m', '5m': '5m', '15m': '15m',
                '1h': '1h', '4h': '4h', '1d': '1d'
            }
            
            interval = tf_map.get(timeframe, '15m')
            url = f"{self.base_url}/api/v3/klines?symbol={pair}&interval={interval}&limit={limit}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    klines = await response.json()
                    
                    # Convert to standardized format
                    formatted_data = []
                    for kline in klines:
                        formatted_data.append({
                            'timestamp': datetime.fromtimestamp(kline[0] / 1000),
                            'open': float(kline[1]),
                            'high': float(kline[2]),
                            'low': float(kline[3]),
                            'close': float(kline[4]),
                            'volume': float(kline[5]),
                            'timeframe': timeframe
                        })
                    
                    return formatted_data
                else:
                    return []
                    
        except Exception as e:
            logging.error(f"❌ Kline fetch error for {pair} {timeframe}: {e}")
            return []
            
    async def get_order_book(self, pair, limit=20):
        """Get order book data"""
        try:
            url = f"{self.base_url}/api/v3/depth?symbol={pair}&limit={limit}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logging.error(f"❌ Order book fetch error for {pair}: {e}")
            return None
            
    async def get_funding_rate(self, pair):
        """Get funding rate for futures (if applicable)"""
        try:
            # For perpetual futures
            if 'USDT' in pair:
                futures_pair = pair.replace('USDT', 'USDT')
                url = f"{self.base_url}/fapi/v1/premiumIndex?symbol={futures_pair}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data.get('lastFundingRate', 0))
            return 0.0
        except Exception as e:
            logging.error(f"❌ Funding rate fetch error for {pair}: {e}")
            return 0.0
            
    async def get_open_interest(self, pair):
        """Get open interest data"""
        try:
            if 'USDT' in pair:
                futures_pair = pair.replace('USDT', 'USDT')
                url = f"{self.base_url}/fapi/v1/openInterest?symbol={futures_pair}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data.get('openInterest', 0))
            return 0.0
        except Exception as e:
            logging.error(f"❌ Open interest fetch error for {pair}: {e}")
            return 0.0
            
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        if self.websocket:
            await self.websocket.close()
            
        logging.info("🔒 Binance API cleanup completed")
