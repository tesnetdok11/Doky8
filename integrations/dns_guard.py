"""
DNS GUARD - Ganti DNS otomatis bila terblokir
"""

import logging
import asyncio
import subprocess
import platform
from datetime import datetime, timedelta

class DNSGuard:
    def __init__(self):
        self.dns_servers = [
            "8.8.8.8",        # Google DNS
            "1.1.1.1",        # Cloudflare DNS
            "9.9.9.9",        # Quad9 DNS
            "208.67.222.222", # OpenDNS
            "8.8.4.4"         # Google DNS Secondary
        ]
        self.current_dns_index = 0
        self.last_switch_time = None
        self.switch_cooldown = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize DNS Guard"""
        logging.info("🛡️ INITIALIZING DNS GUARD...")
        await self._test_current_dns()
        
    async def _test_current_dns(self):
        """Test current DNS connectivity"""
        try:
            # Test DNS resolution
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["nslookup", "google.com"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    ["nslookup", "google.com"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
            if result.returncode == 0:
                logging.info("✅ Current DNS is working")
                return True
            else:
                logging.warning("❌ Current DNS test failed")
                return False
                
        except Exception as e:
            logging.error(f"❌ DNS test error: {e}")
            return False
            
    async def check_and_switch_dns(self):
        """Check DNS and switch if necessary"""
        try:
            # Check if we're in cooldown period
            if (self.last_switch_time and 
                (datetime.utcnow() - self.last_switch_time).total_seconds() < self.switch_cooldown):
                return True
                
            # Test current DNS
            if await self._test_current_dns():
                return True
                
            # DNS is blocked, switch to next server
            await self._switch_dns()
            return await self._test_current_dns()
            
        except Exception as e:
            logging.error(f"❌ DNS check error: {e}")
            return False
            
    async def _switch_dns(self):
        """Switch to next DNS server"""
        try:
            self.current_dns_index = (self.current_dns_index + 1) % len(self.dns_servers)
            new_dns = self.dns_servers[self.current_dns_index]
            
            logging.warning(f"🔄 Switching DNS to: {new_dns}")
            
            system = platform.system()
            
            if system == "Windows":
                await self._set_dns_windows(new_dns)
            elif system == "Linux":
                await self._set_dns_linux(new_dns)
            elif system == "Darwin":  # macOS
                await self._set_dns_macos(new_dns)
            else:
                logging.error(f"❌ Unsupported platform: {system}")
                return
                
            self.last_switch_time = datetime.utcnow()
            logging.info(f"✅ DNS switched to: {new_dns}")
            
        except Exception as e:
            logging.error(f"❌ DNS switch error: {e}")
            
    async def _set_dns_windows(self, dns_server):
        """Set DNS on Windows"""
        try:
            # This requires administrator privileges
            subprocess.run(
                f"netsh interface ip set dns name=\"Ethernet\" static {dns_server}",
                shell=True,
                capture_output=True
            )
        except Exception as e:
            logging.error(f"❌ Windows DNS set error: {e}")
            
    async def _set_dns_linux(self, dns_server):
        """Set DNS on Linux"""
        try:
            # Update resolv.conf (temporary)
            with open("/etc/resolv.conf", "w") as f:
                f.write(f"nameserver {dns_server}\n")
                
        except Exception as e:
            logging.error(f"❌ Linux DNS set error: {e}")
            
    async def _set_dns_macos(self, dns_server):
        """Set DNS on macOS"""
        try:
            # Get current network service
            result = subprocess.run(
                ["networksetup", "-listallnetworkservices"],
                capture_output=True, text=True
            )
            
            services = result.stdout.strip().split('\n')[1:]  # Skip first line
            for service in services:
                if "Wi-Fi" in service or "Ethernet" in service:
                    subprocess.run([
                        "networksetup", "-setdnsservers", service.strip(), dns_server
                    ], capture_output=True)
                    
        except Exception as e:
            logging.error(f"❌ macOS DNS set error: {e}")
            
    async def get_current_dns(self):
        """Get current DNS server"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["ipconfig", "/all"], 
                    capture_output=True, 
                    text=True
                )
                lines = result.stdout.split('\n')
                for line in lines:
                    if "DNS Servers" in line:
                        return line.split(":")[1].strip()
            else:
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        if line.startswith("nameserver"):
                            return line.split()[1]
            return "Unknown"
        except Exception as e:
            logging.error(f"❌ Get DNS error: {e}")
            return "Unknown"
            
    async def monitor_dns_health(self):
        """Monitor DNS health continuously"""
        while True:
            try:
                is_healthy = await self.check_and_switch_dns()
                if not is_healthy:
                    logging.error("🚨 DNS health critical - all servers failed")
                    
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"❌ DNS health monitor error: {e}")
                await asyncio.sleep(30)
                
    async def cleanup(self):
        """Cleanup DNS Guard"""
        # Restore original DNS if possible
        logging.info("🔒 DNS Guard cleanup completed")
