"""
LOGGER - Logging sistem multi-level dengan rotasi
"""

import logging
import logging.handlers
import sys
import os
from datetime import datetime
from pathlib import Path

class DokyOSLogger:
    def __init__(self):
        self.logger = None
        self.setup_complete = False
        
    def setup_logging(self, log_level="INFO", enable_file_logging=True):
        """Setup comprehensive logging system"""
        if self.setup_complete:
            return
            
        try:
            # Create logs directory
            Path("logs").mkdir(exist_ok=True)
            
            # Create logger
            self.logger = logging.getLogger('DokyOS')
            self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            
            # Clear any existing handlers
            self.logger.handlers.clear()
            
            # Create formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            simple_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%H:%M:%S'
            )
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            self.logger.addHandler(console_handler)
            
            if enable_file_logging:
                # Main log file with rotation
                file_handler = logging.handlers.RotatingFileHandler(
                    'logs/dokyos.log',
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(detailed_formatter)
                self.logger.addHandler(file_handler)
                
                # Error log file (only errors and critical)
                error_handler = logging.handlers.RotatingFileHandler(
                    'logs/errors.log',
                    maxBytes=5*1024*1024,  # 5MB
                    backupCount=3,
                    encoding='utf-8'
                )
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(detailed_formatter)
                self.logger.addHandler(error_handler)
                
            self.setup_complete = True
            
            # Log startup message
            self.logger.info("🚀 DokyOS Logger initialized successfully")
            self.logger.info(f"📝 Log level: {log_level}")
            self.logger.info(f"💾 File logging: {'Enabled' if enable_file_logging else 'Disabled'}")
            
        except Exception as e:
            print(f"❌ Logger setup failed: {e}")
            # Fallback to basic logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%H:%M:%S'
            )
            logging.info("🚀 DokyOS Logger (basic) initialized")
            
    def get_logger(self, name=None):
        """Get logger instance"""
        if name:
            return logging.getLogger(f'DokyOS.{name}')
        return self.logger
        
    def log_system_start(self, version, start_time):
        """Log system startup"""
        self.logger.info(f"🎯 DokyOS {version} starting up...")
        self.logger.info(f"⏰ Start time: {start_time}")
        
    def log_system_stop(self, stop_time, uptime):
        """Log system shutdown"""
        self.logger.info(f"🛑 DokyOS shutting down...")
        self.logger.info(f"⏰ Stop time: {stop_time}")
        self.logger.info(f"📊 Total uptime: {uptime}")
        
    def log_signal_generated(self, signal):
        """Log trading signal generation"""
        try:
            pair = signal.get('pair', 'Unknown')
            direction = signal.get('direction', 'Unknown')
            confidence = signal.get('confidence', 0)
            adjusted_confidence = signal.get('adjusted_confidence', confidence)
            
            self.logger.info(
                f"📡 Signal Generated | {pair} {direction} | "
                f"Confidence: {confidence:.1%} | "
                f"Adjusted: {adjusted_confidence:.1%}"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Signal logging error: {e}")
            
    def log_market_analysis(self, analysis_type, pair, result, confidence=0):
        """Log market analysis results"""
        try:
            if confidence > 0:
                self.logger.debug(
                    f"📊 {analysis_type} Analysis | {pair} | "
                    f"Result: {result} | Confidence: {confidence:.1%}"
                )
            else:
                self.logger.debug(
                    f"📊 {analysis_type} Analysis | {pair} | Result: {result}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Analysis logging error: {e}")
            
    def log_performance_metrics(self, metrics):
        """Log performance metrics"""
        try:
            self.logger.info(
                f"📈 Performance | "
                f"CPU: {metrics.get('cpu_percent', 0):.1f}% | "
                f"Memory: {metrics.get('memory_percent', 0):.1f}% | "
                f"Uptime: {metrics.get('uptime_hours', 0):.1f}h"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Performance logging error: {e}")
            
    def log_error_with_context(self, error, context=None, module=None):
        """Log error with context information"""
        try:
            log_message = f"💥 Error"
            
            if module:
                log_message += f" in {module}"
                
            log_message += f": {error}"
            
            if context:
                log_message += f" | Context: {context}"
                
            self.logger.error(log_message)
            
        except Exception as e:
            print(f"❌ Error logging failed: {e}")
            
    def log_api_call(self, api_name, endpoint, status, duration=0):
        """Log API calls"""
        try:
            if status == "success":
                self.logger.debug(
                    f"🔗 API Call | {api_name} {endpoint} | "
                    f"Status: {status} | Duration: {duration:.2f}s"
                )
            else:
                self.logger.warning(
                    f"🔗 API Call | {api_name} {endpoint} | "
                    f"Status: {status} | Duration: {duration:.2f}s"
                )
                
        except Exception as e:
            self.logger.error(f"❌ API call logging error: {e}")
            
    def log_ai_analysis(self, analysis_type, input_data, output_data, duration=0):
        """Log AI analysis activities"""
        try:
            self.logger.debug(
                f"🤖 AI Analysis | {analysis_type} | "
                f"Duration: {duration:.2f}s | "
                f"Input: {len(input_data)} items | "
                f"Output: {len(output_data)} items"
            )
            
        except Exception as e:
            self.logger.error(f"❌ AI analysis logging error: {e}")
            
    def log_data_sync(self, sync_type, items_synced, status, duration=0):
        """Log data synchronization activities"""
        try:
            self.logger.info(
                f"🔄 Data Sync | {sync_type} | "
                f"Items: {items_synced} | "
                f"Status: {status} | "
                f"Duration: {duration:.2f}s"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Data sync logging error: {e}")
            
    def log_security_event(self, event_type, severity, description):
        """Log security events"""
        try:
            if severity == "high":
                self.logger.critical(
                    f"🛡️ Security Event | {event_type} | {description}"
                )
            elif severity == "medium":
                self.logger.warning(
                    f"🛡️ Security Event | {event_type} | {description}"
                )
            else:
                self.logger.info(
                    f"🛡️ Security Event | {event_type} | {description}"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Security event logging error: {e}")
            
    def set_log_level(self, level):
        """Set log level dynamically"""
        try:
            self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
            self.logger.info(f"📝 Log level changed to: {level}")
        except Exception as e:
            self.logger.error(f"❌ Log level change error: {e}")
            
    def cleanup(self):
        """Cleanup logger"""
        try:
            # Flush all handlers
            for handler in self.logger.handlers:
                handler.flush()
                handler.close()
            self.logger.info("🔒 Logger cleanup completed")
        except Exception as e:
            print(f"❌ Logger cleanup error: {e}")

class PerformanceFilter(logging.Filter):
    """Filter for performance-related log messages"""
    
    def filter(self, record):
        # Filter messages that contain performance metrics
        performance_keywords = [
            'performance', 'metrics', 'cpu', 'memory', 'duration', 
            'uptime', 'throughput', 'latency'
        ]
        
        message = record.getMessage().lower()
        return any(keyword in message for keyword in performance_keywords)

# Global logger instance
doky_logger = DokyOSLogger()

def setup_logging(log_level="INFO", enable_file_logging=True):
    """Setup logging (global function)"""
    doky_logger.setup_logging(log_level, enable_file_logging)
    
def get_logger(name=None):
    """Get logger instance (global function)"""
    return doky_logger.get_logger(name)
