"""
DEEPSEEK CONNECTOR - Jembatan antara DokyOS & DeepSeek AI
"""

import logging
import aiohttp
import json
import asyncio
from datetime import datetime
from config.settings import settings

class DeepSeekConnector:
    def __init__(self):
        self.api_key = None  # Jangan langsung assign
        self.base_url = "https://api.deepseek.com/v1"
        self.session = None
        self.enabled = settings.DEEPSEEK_ENABLED
        
    async def initialize(self):
        """Initialize DeepSeek connection"""
        if not self.enabled:
            logging.info("🔕 DeepSeek AI disabled")
            return
            
        logging.info("🧠 INITIALIZING DEEPSEEK CONNECTOR...")
        
        try:
            # Load from settings - SEKARANG SUDAH ADA
            self.api_key = settings.DEEPSEEK_API_KEY
            
            if not self.api_key:
                logging.warning("⚠️ DeepSeek API key not configured")
                self.enabled = False
                return
                
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Test connection
            if await self._test_connection():
                logging.info("✅ DEEPSEEK AI CONNECTED SUCCESSFULLY")
            else:
                logging.error("❌ DEEPSEEK AI CONNECTION FAILED")
                self.enabled = False
                
        except Exception as e:
            logging.error(f"❌ DeepSeek initialization failed: {e}")
            self.enabled = False
            
    # ... rest of the methods remain the same ...            
    async def _test_connection(self):
        """Test DeepSeek API connection"""
        try:
            response = await self._make_request(
                "GET",
                "/models",
                {}
            )
            return response is not None
        except Exception as e:
            logging.error(f"❌ DeepSeek connection test failed: {e}")
            return False
            
    async def _make_request(self, method, endpoint, data):
        """Make request to DeepSeek API"""
        if not self.enabled:
            return None
            
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logging.error(f"❌ DeepSeek API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logging.error(f"❌ DeepSeek request error: {e}")
            return None
            
    async def analyze_market_context(self, market_data, technical_analysis):
        """Analyze market context using DeepSeek AI"""
        if not self.enabled:
            return None
            
        try:
            prompt = self._create_analysis_prompt(market_data, technical_analysis)
            
            response = await self._make_request(
                "POST",
                "/chat/completions",
                {
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": """Anda adalah analis pasar crypto profesional. 
                            Analisis data teknis dan berikan insight tentang:
                            - Struktur pasar dan momentum
                            - Level liquidity yang relevan
                            - Probabilitas pergerakan berikutnya
                            - Konfirmasi sinyal trading
                            Berikan respon dalam format JSON."""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content']
                return self._parse_ai_response(content)
            else:
                return None
                
        except Exception as e:
            logging.error(f"❌ DeepSeek analysis error: {e}")
            return None
            
    def _create_analysis_prompt(self, market_data, technical_analysis):
        """Create analysis prompt for AI"""
        prompt = f"""
        ANALISIS PASAR CRYPTO - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

        DATA PASAR TERKINI:
        {json.dumps(self._summarize_market_data(market_data), indent=2)}

        ANALISIS TEKNIKAL:
        {json.dumps(self._summarize_technical_analysis(technical_analysis), indent=2)}

        PERTANYAAN ANALISIS:
        1. Bagaimana struktur pasar saat ini (trend, support/resistance)?
        2. Di mana zona liquidity kunci yang perlu diperhatikan?
        3. Apa probabilitas pergerakan bullish/bearish dalam 4-6 jam ke depan?
        4. Apakah ada konfirmasi sinyal trading dari analisis multi-timeframe?
        5. Risk management recommendations?

        Berikan respon dalam format JSON dengan struktur:
        {{
            "market_structure": "bullish/bearish/neutral",
            "key_levels": {{
                "support": [level1, level2],
                "resistance": [level1, level2]
            }},
            "liquidity_zones": [
                {{"price": level, "type": "above/below", "strength": "high/medium/low"}}
            ],
            "probability_analysis": {{
                "bullish_probability": 0.0-1.0,
                "bearish_probability": 0.0-1.0,
                "confidence": 0.0-1.0
            }},
            "trading_signals": [
                {{"pair": "BTCUSDT", "direction": "buy/sell", "confidence": 0.0-1.0, "reason": "string"}}
            ],
            "risk_assessment": "high/medium/low",
            "reasoning": "Penjelasan analisis..."
        }}
        """
        return prompt
        
    def _summarize_market_data(self, market_data):
        """Summarize market data for AI analysis"""
        summary = {}
        
        for pair, data in list(market_data.items())[:5]:  # Limit to top 5 pairs
            summary[pair] = {
                'current_price': data.get('current_price', 0),
                'price_change_24h': data.get('price_change_percent_24h', 0),
                'volume_24h': data.get('volume_24h', 0),
                'high_24h': data.get('high_24h', 0),
                'low_24h': data.get('low_24h', 0)
            }
            
        return summary
        
    def _summarize_technical_analysis(self, technical_analysis):
        """Summarize technical analysis for AI"""
        summary = {}
        
        for pair, analysis in list(technical_analysis.items())[:3]:  # Limit to top 3 pairs
            summary[pair] = {
                'trend': analysis.get('primary_trend', 'neutral'),
                'trend_strength': analysis.get('trend_strength', 0),
                'key_levels': analysis.get('key_levels', []),
                'momentum': analysis.get('momentum', 'neutral')
            }
            
        return summary
        
    def _parse_ai_response(self, content):
        """Parse AI response into structured data"""
        try:
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logging.error("❌ No JSON found in AI response")
                return None
                
        except Exception as e:
            logging.error(f"❌ AI response parsing error: {e}")
            return None
            
    async def optimize_signal_confidence(self, signal, market_context):
        """Optimize signal confidence using AI"""
        if not self.enabled:
            return signal
            
        try:
            prompt = self._create_optimization_prompt(signal, market_context)
            
            response = await self._make_request(
                "POST",
                "/chat/completions",
                {
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Anda adalah risk manager trading. Evaluasi sinyal trading dan berikan penyesuaian confidence berdasarkan konteks pasar."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1000
                }
            )
            
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content']
                optimization = self._parse_optimization_response(content)
                
                # Apply optimization to signal
                if optimization:
                    signal['ai_confidence_boost'] = optimization.get('confidence_boost', 0)
                    signal['adjusted_confidence'] = min(
                        signal['confidence'] + optimization.get('confidence_boost', 0), 
                        0.95
                    )
                    signal['ai_reasoning'] = optimization.get('reasoning', '')
                    
            return signal
            
        except Exception as e:
            logging.error(f"❌ Signal optimization error: {e}")
            return signal
            
    def _create_optimization_prompt(self, signal, market_context):
        """Create optimization prompt"""
        return f"""
        EVALUASI SINYAL TRADING:
        
        Sinyal: {signal}
        
        Konteks Pasar: {market_context}
        
        Evaluasi:
        1. Apakah sinyal ini sesuai dengan struktur pasar?
        2. Bagaimana risk-reward ratio?
        3. Apakah ada konfirmasi dari faktor fundamental/teknikal?
        4. Rekomendasi penyesuaian confidence (-0.2 hingga +0.2)
        
        Format respons JSON:
        {{
            "confidence_boost": -0.1,
            "reasoning": "Analisis...",
            "risk_adjustment": "increase/decrease/maintain"
        }}
        """
        
    def _parse_optimization_response(self, content):
        """Parse optimization response"""
        try:
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            return None
        except:
            return None
            
    async def cleanup(self):
        """Cleanup DeepSeek connection"""
        if self.session:
            await self.session.close()
        logging.info("🔒 DeepSeek connector cleanup completed")
