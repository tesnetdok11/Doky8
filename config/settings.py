"""
DOKYOS SYSTEM SETTINGS & PARAMETERS
"""

import os
from datetime import datetime

class Settings:
    """Main system settings"""
    
    # ===== SYSTEM CONFIG =====
    SYSTEM_NAME = "DokyOS"
    VERSION = "V23"
    TIMEZONE = os.getenv("TIMEZONE", "UTC")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # ===== RUNTIME CONFIG =====
    BASE_CYCLE_TIME = 2.0  # detik antara cycle
    MAX_CYCLE_TIME = 10.0  # maksimal cycle time
    HEARTBEAT_INTERVAL = 300  # detik
    
    # ===== TRADING PARAMETERS =====
    DEFAULT_RR_RATIO = 3.0
    MIN_CONFIDENCE = 0.80
    MAX_RISK_PERCENT = 3.0
    MIN_RISK_PERCENT = 1.0
    
    # ===== MARKET ANALYSIS =====
    ENABLED_TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"]
    PRIMARY_TIMEFRAME = "15m"
    CONFIRMATION_TIMEFRAMES = ["5m", "15m", "1h"]
    
    # ===== SESSION TIMES (UTC) =====
    ASIA_SESSION = {"start": 0, "end": 8}      # 00:00 - 08:00 UTC
    LONDON_SESSION = {"start": 7, "end": 16}   # 07:00 - 16:00 UTC  
    NEWYORK_SESSION = {"start": 13, "end": 22} # 13:00 - 22:00 UTC
    
    # ===== AI PARAMETERS =====
    DEEPSEEK_ENABLED = True
    AI_CONFIDENCE_BOOST = 0.15
    LEARNING_CYCLE_HOURS = 24
    
    # ===== RISK MANAGEMENT =====
    MAX_DRAWDOWN_PERCENT = 5.0
    DAILY_LOSS_LIMIT = 2.0
    POSITION_SIZING = "volatility"
    
    # ===== NOTIFICATIONS =====
    ENABLE_TELEGRAM = True
    ENABLE_LOGGING = True
    ENABLE_GITHUB_SYNC = True
    
    # ===== API CONFIGURATION =====
    # Binance API
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")
    BINANCE_TIMEOUT = 10
    
    # OKX API - TAMBAHKAN INI
    OKX_API_KEY = os.getenv("OKX_API_KEY", "")
    OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY", "") 
    OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE", "")
    OKX_TIMEOUT = 10
    
    # Telegram API - TAMBAHKAN INI
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    TELEGRAM_TIMEOUT = 5
    
    # GitHub API - TAMBAHKAN INI
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "")
    
    # DeepSeek AI API - TAMBAHKAN INI
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    
    # ===== SECURITY CONFIG =====
    ENCRYPTION_ENABLED = True
    AUTO_RECOVERY = True
    DNS_FAILOVER = True

    def __init__(self):
        """Initialize settings and validate required APIs"""
        self.validate_required_settings()
    
    def validate_required_settings(self):
        """Validate that required settings are present"""
        missing_settings = []
        
        # Check required APIs
        if self.ENABLE_TELEGRAM and not self.TELEGRAM_BOT_TOKEN:
            missing_settings.append("TELEGRAM_BOT_TOKEN")
            
        if self.ENABLE_GITHUB_SYNC and not self.GITHUB_TOKEN:
            missing_settings.append("GITHUB_TOKEN")
            
        if self.DEEPSEEK_ENABLED and not self.DEEPSEEK_API_KEY:
            missing_settings.append("DEEPSEEK_API_KEY")
            
        if missing_settings:
            print(f"⚠️ WARNING: Missing required settings: {missing_settings}")
            print("   Some features may not work properly.")

# Global settings instance
settings = Settings()

def get_current_session():
    """Get current market session"""
    current_hour = datetime.utcnow().hour
    
    if Settings.ASIA_SESSION["start"] <= current_hour < Settings.ASIA_SESSION["end"]:
        return "ASIA"
    elif Settings.LONDON_SESSION["start"] <= current_hour < Settings.LONDON_SESSION["end"]:
        return "LONDON" 
    elif Settings.NEWYORK_SESSION["start"] <= current_hour < Settings.NEWYORK_SESSION["end"]:
        return "NEWYORK"
    else:
        return "GLOBAL"

def get_session_parameters(session):
    """Get parameters for specific session"""
    session_params = {
        "ASIA": {
            "volatility": "low",
            "recommended_pairs": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
            "analysis_intensity": "medium"
        },
        "LONDON": {
            "volatility": "high", 
            "recommended_pairs": ["BTCUSDT", "ETHUSDT", "XRPUSDT", "ADAUSDT"],
            "analysis_intensity": "high"
        },
        "NEWYORK": {
            "volatility": "high",
            "recommended_pairs": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOTUSDT"],
            "analysis_intensity": "high"
        },
        "GLOBAL": {
            "volatility": "medium",
            "recommended_pairs": ["BTCUSDT", "ETHUSDT"],
            "analysis_intensity": "low"
        }
    }
    return session_params.get(session, session_params["GLOBAL"])
