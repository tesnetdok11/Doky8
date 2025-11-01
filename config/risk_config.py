"""
RISK MANAGEMENT CONFIGURATION
"""

from config.settings import settings

class RiskConfig:
    """Risk management configuration"""
    
    @staticmethod
    def calculate_position_size(balance, risk_percent, stop_loss_pips):
        """
        Calculate position size based on risk
        balance: account balance
        risk_percent: risk percentage (1-3%)
        stop_loss_pips: stop loss in pips
        """
        risk_amount = balance * (risk_percent / 100)
        position_size = risk_amount / (stop_loss_pips * 0.0001)  # Simplified
        return min(position_size, balance * 0.1)  # Max 10% of balance
    
    @staticmethod
    def calculate_stop_loss(entry_price, direction, volatility):
        """Calculate dynamic stop loss"""
        if direction == "BUY":
            if volatility == "high":
                return entry_price * 0.98  # 2% stop loss
            elif volatility == "medium":
                return entry_price * 0.99  # 1% stop loss
            else:
                return entry_price * 0.995  # 0.5% stop loss
        else:  # SELL
            if volatility == "high":
                return entry_price * 1.02  # 2% stop loss
            elif volatility == "medium":
                return entry_price * 1.01  # 1% stop loss
            else:
                return entry_price * 1.005  # 0.5% stop loss
    
    @staticmethod
    def calculate_take_profit(entry_price, direction, rr_ratio, stop_loss):
        """Calculate take profit based on RR ratio"""
        if direction == "BUY":
            risk = entry_price - stop_loss
            return entry_price + (risk * rr_ratio)
        else:  # SELL
            risk = stop_loss - entry_price
            return entry_price - (risk * rr_ratio)
    
    @staticmethod
    def validate_trade_signal(signal_confidence, current_drawdown, daily_loss):
        """Validate if trade should be executed"""
        if signal_confidence < settings.MIN_CONFIDENCE:
            return False, "Confidence too low"
            
        if current_drawdown >= settings.MAX_DRAWDOWN_PERCENT:
            return False, "Max drawdown reached"
            
        if daily_loss >= settings.DAILY_LOSS_LIMIT:
            return False, "Daily loss limit reached"
            
        return True, "Valid signal"

# Global risk manager instance
risk_manager = RiskConfig()
