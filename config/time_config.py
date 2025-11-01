"""
TIME CONFIG - Konfigurasi zona waktu dan sinkronisasi
"""

import pytz
from datetime import datetime
from config.settings import settings

class TimeConfig:
    # Timezone configuration
    TIMEZONE = pytz.timezone(settings.TIMEZONE)
    
    # Market session times (UTC)
    MARKET_SESSIONS = {
        "ASIA": {"open": 0, "close": 8},
        "LONDON": {"open": 7, "close": 16},
        "NEWYORK": {"open": 13, "close": 22}
    }
    
    @staticmethod
    def get_utc_time():
        """Get current UTC time"""
        return datetime.utcnow()
        
    @staticmethod
    def get_local_time():
        """Get local time based on configured timezone"""
        utc_time = datetime.utcnow()
        return utc_time.replace(tzinfo=pytz.utc).astimezone(TimeConfig.TIMEZONE)
        
    @staticmethod
    def format_timestamp(dt, include_timezone=True):
        """Format datetime to standard string format"""
        if include_timezone:
            return dt.isoformat()
        else:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
            
    @staticmethod
    def is_market_open():
        """Check if any market session is currently open"""
        current_hour = datetime.utcnow().hour
        for session, times in TimeConfig.MARKET_SESSIONS.items():
            if times["open"] <= current_hour < times["close"]:
                return True
        return False
