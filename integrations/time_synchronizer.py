"""
TIME SYNCHRONIZER - Sinkronisasi waktu via NTP/Google
"""

import logging
import asyncio
import aiohttp
import socket
import struct
import time
from datetime import datetime, timedelta
from config import settings

class TimeSynchronizer:
    def __init__(self):
        self.ntp_servers = [
            "pool.ntp.org",
            "time.google.com", 
            "time.windows.com",
            "time.apple.com",
            "ntp.ubuntu.com"
        ]
        self.time_difference = 0
        self.last_sync = None
        self.sync_interval = 3600  # 1 hour
        
    async def initialize(self):
        """Initialize time synchronizer"""
        logging.info("⏰ INITIALIZING TIME SYNCHRONIZER...")
        
        # Initial sync
        success = await self.sync_time()
        if success:
            logging.info("✅ TIME SYNCHRONIZATION SUCCESSFUL")
        else:
            logging.error("❌ TIME SYNCHRONIZATION FAILED")
            
    async def sync_time(self):
        """Synchronize system time with NTP servers"""
        for server in self.ntp_servers:
            try:
                ntp_time = await self._get_ntp_time(server)
                if ntp_time:
                    system_time = datetime.utcnow()
                    self.time_difference = (ntp_time - system_time).total_seconds()
                    self.last_sync = datetime.utcnow()
                    
                    logging.info(f"✅ Time synced with {server}, difference: {self.time_difference:.3f}s")
                    return True
                    
            except Exception as e:
                logging.warning(f"⚠️ NTP sync failed with {server}: {e}")
                continue
                
        # Fallback to HTTP time
        try:
            http_time = await self._get_http_time()
            if http_time:
                system_time = datetime.utcnow()
                self.time_difference = (http_time - system_time).total_seconds()
                self.last_sync = datetime.utcnow()
                
                logging.info(f"✅ Time synced via HTTP, difference: {self.time_difference:.3f}s")
                return True
                
        except Exception as e:
            logging.error(f"❌ HTTP time sync failed: {e}")
            
        return False
        
    async def _get_ntp_time(self, server):
        """Get time from NTP server"""
        try:
            # NTP protocol implementation
            ntp_port = 123
            ntp_data = b'\x1b' + 47 * b'\0'
            
            # Create socket and set timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # Send NTP request
            sock.sendto(ntp_data, (server, ntp_port))
            data, address = sock.recvfrom(1024)
            sock.close()
            
            if data:
                # Parse NTP response
                ntp_timestamp = struct.unpack('!12I', data)[10]
                ntp_time = datetime(1900, 1, 1) + timedelta(seconds=ntp_timestamp - 2208988800)
                return ntp_time
                
        except Exception as e:
            logging.error(f"❌ NTP query error for {server}: {e}")
            return None
            
    async def _get_http_time(self):
        """Get time from HTTP headers (fallback)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.google.com') as response:
                    if 'date' in response.headers:
                        http_time = datetime.strptime(
                            response.headers['date'], 
                            '%a, %d %b %Y %H:%M:%S GMT'
                        )
                        return http_time
            return None
            
        except Exception as e:
            logging.error(f"❌ HTTP time query error: {e}")
            return None
            
    def get_synchronized_time(self):
        """Get synchronized UTC time"""
        base_time = datetime.utcnow()
        if self.time_difference != 0:
            return base_time + timedelta(seconds=self.time_difference)
        return base_time
        
    def get_time_difference(self):
        """Get current time difference"""
        return self.time_difference
        
    def is_synchronized(self):
        """Check if time is synchronized"""
        return (self.last_sync is not None and 
                (datetime.utcnow() - self.last_sync).total_seconds() < self.sync_interval)
                
    async def continuous_sync(self):
        """Continuous time synchronization"""
        while True:
            try:
                if not self.is_synchronized():
                    await self.sync_time()
                    
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logging.error(f"❌ Continuous sync error: {e}")
                await asyncio.sleep(60)
                
    async def validate_exchange_timestamps(self, exchange_data):
        """Validate exchange timestamps against synchronized time"""
        try:
            if not exchange_data:
                return True
                
            current_time = self.get_synchronized_time()
            
            for pair_data in exchange_data.values():
                if 'timestamp' in pair_data:
                    data_time = pair_data['timestamp']
                    if isinstance(data_time, str):
                        data_time = datetime.fromisoformat(data_time.replace('Z', '+00:00'))
                    
                    time_diff = (current_time - data_time).total_seconds()
                    
                    # Allow up to 10 seconds difference for exchange data
                    if abs(time_diff) > 10:
                        logging.warning(f"⚠️ Exchange data timestamp difference: {time_diff:.1f}s")
                        return False
                        
            return True
            
        except Exception as e:
            logging.error(f"❌ Timestamp validation error: {e}")
            return False
            
    async def get_precise_timestamp(self):
        """Get precise timestamp for logging"""
        synchronized_time = self.get_synchronized_time()
        return {
            'iso_format': synchronized_time.isoformat() + 'Z',
            'timestamp': synchronized_time.timestamp(),
            'human_readable': synchronized_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' UTC'
        }
        
    async def cleanup(self):
        """Cleanup time synchronizer"""
        logging.info("🔒 Time synchronizer cleanup completed")
