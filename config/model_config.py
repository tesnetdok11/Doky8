"""
MODEL CONFIG - Konfigurasi parameter AI dan model
"""

from config.settings import settings

class ModelConfig:
    # DeepSeek AI Configuration
    DEEPSEEK = {
        "model": "deepseek-chat",
        "temperature": 0.3,
        "max_tokens": 2000,
        "timeout": 30
    }
    
    # Machine Learning Parameters
    ML_PARAMS = {
        "learning_rate": 0.001,
        "batch_size": 32,
        "training_epochs": 100,
        "validation_split": 0.2
    }
    
    # Feature Engineering
    FEATURES = {
        "technical_indicators": ["sma", "ema", "rsi", "macd", "bollinger"],
        "price_features": ["open", "high", "low", "close", "volume"],
        "derived_features": ["price_change", "volatility", "momentum"]
    }
    
    # Model Paths
    PATHS = {
        "model_save": "models/",
        "training_data": "data/training/",
        "model_checkpoints": "models/checkpoints/"
    }
