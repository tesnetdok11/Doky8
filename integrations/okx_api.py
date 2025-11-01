"""
OKX API - Koneksi data cadangan OKX
"""

import logging
import asyncio
import aiohttp
import hmac
import hashlib
import base64
import json
from datetime import datetime
from config.settings import settings
from config.pairs import TOP_25_PAIRS

class OKXAPI:
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.api_key = None  # Jangan langsung assign, tunggu initialize
        self.secret_key = None
        self.passphrase = None
        self.session = None
        
    async def initialize(self):
        """Initialize OKX API connection"""
        logging.info("🔗 INITIALIZING OKX API...")
        
        # Load API keys from settings - SEKARANG SUDAH ADA
        self.api_key = settings.OKX_API_KEY
        self.secret_key = settings.OKX_SECRET_KEY
        self.passphrase = settings.OKX_PASSPHRASE
        
        # Check if API keys are available
        if not self.api_key or not self.secret_key:
            logging.warning("⚠️ OKX API keys not configured - OKX will be disabled")
            return False
            
        # Create aiohttp session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.OKX_TIMEOUT)
        )
        
        # Test connection
        if await self._test_connection():
            logging.info("✅ OKX API CONNECTED SUCCESSFULLY")
            return True
        else:
            logging.error("❌ OKX API CONNECTION FAILED")
            return False
            
    async def _test_connection(self):
        """Test API connection"""
        try:
            # Simple public endpoint to test connection
            url = f"{self.base_url}/api/v5/market/tickers?instType=SPOT"
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception as e:
            logging.error(f"❌ OKX connection test failed: {e}")
            return False
            
    async def fetch_market_data(self):
        """Fetch market data from OKX as backup"""
        # Jika API keys tidak tersedia, return empty dict
        if not self.api_key or not self.secret_key:
            return {}
            
        market_data = {}
        
        try:
            tasks = []
            for pair in TOP_25_PAIRS:
                # Convert Binance pair format to OKX format
                okx_pair = self._convert_pair_format(pair)
                if okx_pair:
                    task = asyncio.create_task(self._fetch_pair_data(okx_pair, pair))
                    tasks.append(task)
                    
            # Fetch all pairs concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for original_pair, result in zip(TOP_25_PAIRS, results):
                if isinstance(result, Exception):
                    logging.error(f"❌ Error fetching {original_pair} from OKX: {result}")
                    continue
                if result:
                    market_data[original_pair] = result
                    
            logging.info(f"📊 Fetched data for {len(market_data)} pairs from OKX")
            return market_data
            
        except Exception as e:
            logging.error(f"❌ OKX market data fetch error: {e}")
            return {}
            
    def _generate_signature(self, timestamp, method, request_path, body=""):
        """Generate OKX API signature"""
        try:
            message = timestamp + method + request_path + body
            mac = hmac.new(
                bytes(self.secret_key, 'utf-8'),
                bytes(message, 'utf-8'),
                hashlib.sha256
            )
            return base64.b64encode(mac.digest()).decode()
        except Exception as e:
            logging.error(f"❌ Signature generation error: {e}")
            return ""
            
    async def fetch_market_data(self):
        """Fetch market data from OKX as backup"""
        market_data = {}
        
        try:
            tasks = []
            for pair in TOP_25_PAIRS:
                # Convert Binance pair format to OKX format
                okx_pair = self._convert_pair_format(pair)
                if okx_pair:
                    task = asyncio.create_task(self._fetch_pair_data(okx_pair, pair))
                    tasks.append(task)
                    
            # Fetch all pairs concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for original_pair, result in zip(TOP_25_PAIRS, results):
                if isinstance(result, Exception):
                    logging.error(f"❌ Error fetching {original_pair} from OKX: {result}")
                    continue
                if result:
                    market_data[original_pair] = result
                    
            logging.info(f"📊 Fetched data for {len(market_data)} pairs from OKX")
            return market_data
            
        except Exception as e:
            logging.error(f"❌ OKX market data fetch error: {e}")
            return {}
            
    def _convert_pair_format(self, binance_pair):
        """Convert Binance pair format to OKX format"""
        # OKX uses format like BTC-USDT, ETH-USDT
        if binance_pair.endswith('USDT'):
            coin = binance_pair.replace('USDT', '')
            return f"{coin}-USDT"
        return None
        
    async def _fetch_pair_data(self, okx_pair, original_pair):
        """Fetch data for single pair from OKX"""
        try:
            # Get ticker data
            ticker_url = f"{self.base_url}/api/v5/market/ticker?instId={okx_pair}"
            async with self.session.get(ticker_url) as response:
                if response.status == 200:
                    ticker_data = await response.json()
                    if ticker_data['code'] == '0':
                        ticker_info = ticker_data['data'][0]
                        
            # Get OHLCV data
            ohlcv_data = {}
            for tf in settings.ENABLED_TIMEFRAMES:
                kline_data = await self._fetch_candles(okx_pair, tf)
                if kline_data:
                    ohlcv_data[tf] = kline_data
                    
            return {
                'pair': original_pair,
                'current_price': float(ticker_info['last']),
                'price_change_24h': float(ticker_info['last']) - float(ticker_info['open24h']),
                'price_change_percent_24h': (float(ticker_info['last']) - float(ticker_info['open24h'])) / float(ticker_info['open24h']) * 100,
                'volume_24h': float(ticker_info['vol24h']),
                'high_24h': float(ticker_info['high24h']),
                'low_24h': float(ticker_info['low24h']),
                'ohlcv': ohlcv_data,
                'timestamp': datetime.utcnow(),
                'exchange': 'okx'
            }
            
        except Exception as e:
            logging.error(f"❌ OKX pair data fetch error for {okx_pair}: {e}")
            return None
            
    async def _fetch_candles(self, pair, timeframe, limit=100):
        """Fetch candle data from OKX"""
        try:
            # Map timeframe to OKX bar
            tf_map = {
                '1m': '1m', '5m': '5m', '15m': '15m',
                '1h': '1H', '4h': '4H', '1d': '1D'
            }
            
            bar = tf_map.get(timeframe, '15m')
            url = f"{self.base_url}/api/v5/market/candles?instId={pair}&bar={bar}&limit={limit}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    candles_data = await response.json()
                    if candles_data['code'] == '0':
                        candles = candles_data['data']
                        
                        # Convert to standardized format
                        formatted_data = []
                        for candle in candles:
                            formatted_data.append({
                                'timestamp': datetime.fromtimestamp(int(candle[0]) / 1000),
                                'open': float(candle[1]),
                                'high': float(candle[2]),
                                'low': float(candle[3]),
                                'close': float(candle[4]),
                                'volume': float(candle[5]),
                                'timeframe': timeframe
                            })
                        
                        return formatted_data
                return []
                
        except Exception as e:
            logging.error(f"❌ OKX candles fetch error for {pair} {timeframe}: {e}")
            return []
            
    async def get_funding_rate(self, pair):
        """Get funding rate from OKX"""
        try:
            okx_pair = self._convert_pair_format(pair)
            if okx_pair and '-USDT' in okx_pair:
                # For perpetual swap
                swap_pair = okx_pair.replace('-USDT', '-USDT-SWAP')
                url = f"{self.base_url}/api/v5/public/funding-rate?instId={swap_pair}"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['code'] == '0' and data['data']:
                            return float(data['data'][0]['fundingRate'])
            return 0.0
        except Exception as e:
            logging.error(f"❌ OKX funding rate fetch error for {pair}: {e}")
            return 0.0
            
    async def get_open_interest(self, pair):
        """Get open interest from OKX"""
        try:
            okx_pair = self._convert_pair_format(pair)
            if okx_pair and '-USDT' in okx_pair:
                swap_pair = okx_pair.replace('-USDT', '-USDT-SWAP')
                url = f"{self.base_url}/api/v5/public/open-interest?instId={swap_pair}"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['code'] == '0' and data['data']:
                            return float(data['data'][0]['oi'])
            return 0.0
        except Exception as e:
            logging.error(f"❌ OKX open interest fetch error for {pair}: {e}")
            return 0.0
            
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        logging.info("🔒 OKX API cleanup completed")
