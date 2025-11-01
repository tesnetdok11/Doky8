"""
TELEGRAM AI - Output sinyal & notifikasi ke Telegram
"""

import logging
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime
from config.settings import settings

class TelegramAI:
    def __init__(self):
        self.bot = None
        self.chat_id = None
        self.enabled = settings.ENABLE_TELEGRAM
        
    async def initialize(self):
        """Initialize Telegram bot"""
        if not self.enabled:
            logging.info("🔕 Telegram notifications disabled")
            return
            
        logging.info("🤖 INITIALIZING TELEGRAM BOT...")
        
        try:
            # Load from settings - SEKARANG SUDAH ADA
            bot_token = settings.TELEGRAM_BOT_TOKEN
            self.chat_id = settings.TELEGRAM_CHAT_ID
            
            if not bot_token or not self.chat_id:
                logging.warning("⚠️ Telegram bot token or chat ID not configured")
                self.enabled = False
                return
                
            self.bot = Bot(token=bot_token)
            
            # Test connection
            me = await self.bot.get_me()
            logging.info(f"✅ TELEGRAM BOT CONNECTED: @{me.username}")
            
        except Exception as e:
            logging.error(f"❌ Telegram bot initialization failed: {e}")
            self.enabled = False
            
    # ... rest of the methods remain the same ...            
    async def send_signals(self, signals):
        """Send trading signals to Telegram"""
        if not self.enabled or not signals:
            return
            
        try:
            for signal in signals:
                message = self._format_signal_message(signal)
                await self._send_message(message)
                
                # Add small delay to avoid rate limits
                await asyncio.sleep(1)
                
        except Exception as e:
            logging.error(f"❌ Error sending signals to Telegram: {e}")
            
    async def send_message(self, text):
        """Send simple text message"""
        if not self.enabled:
            return
            
        try:
            await self._send_message(text)
        except Exception as e:
            logging.error(f"❌ Error sending message to Telegram: {e}")
            
    async def _send_message(self, text):
        """Internal method to send message"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        except Exception as e:
            logging.error(f"❌ Telegram send message error: {e}")
            
    def _format_signal_message(self, signal):
        """Format signal into Telegram message"""
        try:
            pair = signal['pair']
            direction = signal['direction']
            confidence = signal['confidence']
            entry = signal['entry']
            stop_loss = signal['stop_loss']
            take_profit = signal['take_profit']
            reason = signal.get('reason', 'High probability setup')
            timeframe = signal.get('timeframe', '15m')
            
            # Emoji based on direction and confidence
            if direction == "BUY":
                emoji = "🟢" if confidence > 0.85 else "🟡"
            else:
                emoji = "🔴" if confidence > 0.85 else "🟠"
                
            # Risk reward info
            risk = abs(entry - stop_loss)
            reward = abs(take_profit - entry)
            rr_ratio = round(reward / risk, 2) if risk > 0 else 0
            
            message = f"""
{emoji} **DOKYOS SIGNAL** {emoji}

**Pair:** `{pair}`
**Direction:** `{direction}`
**Timeframe:** `{timeframe}`
**Confidence:** `{confidence:.1%}`

**Entry:** `{entry:.6f}`
**Stop Loss:** `{stop_loss:.6f}`
**Take Profit:** `{take_profit:.6f}`
**R/R Ratio:** `{rr_ratio}:1`

**Reason:** {reason}

*Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""
            return message
            
        except Exception as e:
            logging.error(f"❌ Error formatting signal message: {e}")
            return f"Signal error: {e}"
            
    async def send_alert(self, alert_type, message, priority="medium"):
        """Send alert message with priority"""
        if not self.enabled:
            return
            
        try:
            priority_emojis = {
                "low": "ℹ️",
                "medium": "⚠️", 
                "high": "🚨",
                "critical": "🔴"
            }
            
            emoji = priority_emojis.get(priority, "⚠️")
            formatted_message = f"{emoji} **{alert_type.upper()}** {emoji}\n\n{message}"
            
            await self._send_message(formatted_message)
            
        except Exception as e:
            logging.error(f"❌ Error sending alert to Telegram: {e}")
            
    async def send_performance_report(self, report_data):
        """Send performance report"""
        if not self.enabled:
            return
            
        try:
            total_signals = report_data.get('total_signals', 0)
            successful_signals = report_data.get('successful_signals', 0)
            accuracy = report_data.get('accuracy', 0)
            total_pnl = report_data.get('total_pnl', 0)
            
            message = f"""
📊 **DOKYOS PERFORMANCE REPORT**

**Period:** {report_data.get('period', 'Daily')}
**Total Signals:** `{total_signals}`
**Successful:** `{successful_signals}`
**Accuracy:** `{accuracy:.1%}`
**Total PnL:** `{total_pnl:.2f}%`

**Top Performing Pairs:**
"""
            
            top_pairs = report_data.get('top_pairs', [])
            for pair, perf in top_pairs[:5]:
                message += f"• `{pair}`: `{perf:.1f}%`\n"
                
            await self._send_message(message)
            
        except Exception as e:
            logging.error(f"❌ Error sending performance report: {e}")
            
    async def cleanup(self):
        """Cleanup Telegram bot"""
        if self.bot:
            # Telegram bot doesn't need explicit cleanup
            pass
        logging.info("🔒 Telegram cleanup completed")
