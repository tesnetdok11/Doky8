# config/dynamic_config.py - Dynamic configuration system
import json
import os
from datetime import datetime
from config.settings import settings

class DynamicConfig:
    def __init__(self):
        self.config_file = "config/dynamic_settings.json"
        self.last_update = None
        self.config_cache = {}
        
    async def initialize(self):
        """Initialize dynamic configuration"""
        await self.load_config()
        
    async def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config_cache = json.load(f)
                self.last_update = datetime.utcnow()
                logging.info("✅ Dynamic configuration loaded")
            else:
                await self.create_default_config()
        except Exception as e:
            logging.error(f"❌ Config load error: {e}")
            await self.create_default_config()
            
    async def create_default_config(self):
        """Create default dynamic configuration"""
        self.config_cache = {
            "performance_metrics": {
                "avg_cycle_time": 2.0,
                "error_rate": 0.0,
                "signal_accuracy": 0.85
            },
            "adaptive_settings": {
                "market_volatility_adjustment": 1.0,
                "analysis_intensity": "normal",
                "sleep_time_multiplier": 1.0
            },
            "circuit_breakers": {
                "max_consecutive_errors": 5,
                "api_call_timeout": 30,
                "analysis_timeout": 60
            },
            "optimization_flags": {
                "enable_aggressive_analysis": False,
                "reduce_volume_analysis": False,
                "prioritize_majors": True
            }
        }
        await self.save_config()
        
    async def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config_cache, f, indent=2)
            self.last_update = datetime.utcnow()
        except Exception as e:
            logging.error(f"❌ Config save error: {e}")
            
    async def update_setting(self, category, key, value):
        """Update a configuration setting"""
        if category not in self.config_cache:
            self.config_cache[category] = {}
        self.config_cache[category][key] = value
        await self.save_config()
        
    async def get_adaptive_sleep_time(self, base_time):
        """Get adaptive sleep time based on performance"""
        multiplier = self.config_cache["adaptive_settings"]["sleep_time_multiplier"]
        return base_time * multiplier
        
    async def adjust_for_volatility(self, base_confidence):
        """Adjust confidence based on market volatility"""
        volatility_adj = self.config_cache["adaptive_settings"]["market_volatility_adjustment"]
        return base_confidence * volatility_adj

# Global instance
dynamic_config = DynamicConfig()
