"""
TOP 25 CRYPTO PAIRS CONFIGURATION
"""

# Top 25 Crypto Pairs by Volume (Binance)
TOP_25_PAIRS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT",
    "MATICUSDT", "LTCUSDT", "UNIUSDT", "ATOMUSDT", "XLMUSDT",
    "ETCUSDT", "FILUSDT", "APTUSDT", "NEARUSDT", "ALGOUSDT", 
    "ARBUSDT", "VETUSDT", "AAVEUSDT", "EOSUSDT", "XMRUSDT"
]

# Pair Categories
CATEGORIES = {
    "MAJORS": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    "MID_CAPS": ["SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT"],
    "DEFI": ["UNIUSDT", "LINKUSDT", "AAVEUSDT"],
    "LAYER1": ["DOTUSDT", "ATOMUSDT", "NEARUSDT", "ALGOUSDT", "APTUSDT"]
}

# Pair-specific settings
PAIR_SETTINGS = {
    "BTCUSDT": {
        "volatility": "high",
        "spread": "low", 
        "recommended_timeframes": ["15m", "1h", "4h"]
    },
    "ETHUSDT": {
        "volatility": "high",
        "spread": "low",
        "recommended_timeframes": ["15m", "1h", "4h"]
    },
    # ... settings for other pairs
}

def get_pairs_by_volatility(level="medium"):
    """Get pairs by volatility level"""
    volatility_map = {
        "low": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
        "medium": ["ADAUSDT", "XRPUSDT", "LTCUSDT", "DOTUSDT"],
        "high": ["SOLUSDT", "AVAXUSDT", "MATICUSDT", "DOGEUSDT"]
    }
    return volatility_map.get(level, TOP_25_PAIRS)

def get_session_pairs(session):
    """Get optimal pairs for current session"""
    session_pairs = {
        "ASIA": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT"],
        "LONDON": TOP_25_PAIRS[:15],
        "NEWYORK": TOP_25_PAIRS
    }
    return session_pairs.get(session, TOP_25_PAIRS)
