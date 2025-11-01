"""
DECISION MAKER - Sistem pengambilan keputusan BUY/SELL/WAIT
"""

import logging
from datetime import datetime
from config import settings
from config.risk_config import risk_manager

class DecisionMaker:
    def __init__(self):
        self.setup_decision_engine()
        
    def setup_decision_engine(self):
        """Setup mesin keputusan"""
        self.decision_rules = {
            'BUY': self._buy_conditions,
            'SELL': self._sell_conditions, 
            'WAIT': self._wait_conditions
        }
        
    async def initialize(self):
        """Initialize decision maker"""
        logging.info("🤖 INITIALIZING DECISION MAKER...")
        
    async def generate(self, analysis):
        """Generate keputusan trading"""
        if not analysis:
            return []
            
        decisions = []
        
        # Analisis untuk setiap pair
        for pair in analysis.get('probability', {}).keys():
            decision = await self._evaluate_pair(pair, analysis)
            if decision:
                decisions.append(decision)
                
        return decisions
        
    async def _evaluate_pair(self, pair, analysis):
        """Evaluasi pair untuk keputusan trading"""
        try:
            # Dapatkan probabilitas untuk pair
            prob_data = analysis['probability'].get(pair, {})
            confidence = prob_data.get('confidence', 0)
            
            # Validasi risk management
            is_valid, reason = risk_manager.validate_trade_signal(
                confidence, 0, 0  # drawdown dan daily loss sementara 0
            )
            
            if not is_valid:
                return None
                
            # Tentukan arah trading
            direction = self._determine_direction(prob_data, analysis['structure'].get(pair, {}))
            
            if direction == "WAIT":
                return None
                
            # Hitung entry, stop loss, take profit
            price_data = analysis['structure'][pair].get('price_action', {})
            entry = price_data.get('close', 0)
            volatility = analysis['structure'][pair].get('volatility', 'medium')
            
            stop_loss = risk_manager.calculate_stop_loss(entry, direction, volatility)
            take_profit = risk_manager.calculate_take_profit(
                entry, direction, settings.DEFAULT_RR_RATIO, stop_loss
            )
            
            # Buat sinyal
            signal = {
                'pair': pair,
                'direction': direction,
                'entry': entry,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'timestamp': datetime.utcnow(),
                'timeframe': analysis['structure'][pair].get('primary_tf', '15m'),
                'reason': prob_data.get('reason', 'High probability setup')
            }
            
            return signal
            
        except Exception as e:
            logging.error(f"❌ Decision evaluation error for {pair}: {e}")
            return None
            
    def _determine_direction(self, prob_data, structure_data):
        """Tentukan arah trading berdasarkan probabilitas dan struktur"""
        buy_prob = prob_data.get('buy_probability', 0)
        sell_prob = prob_data.get('sell_probability', 0)
        
        min_confidence = settings.MIN_CONFIDENCE
        
        if buy_prob >= min_confidence and buy_prob > sell_prob:
            return "BUY"
        elif sell_prob >= min_confidence and sell_prob > buy_prob:
            return "SELL"
        else:
            return "WAIT"
            
    def _buy_conditions(self, analysis):
        """Kondisi untuk sinyal BUY"""
        # Implementasi kondisi BUY
        pass
        
    def _sell_conditions(self, analysis):
        """Kondisi untuk sinyal SELL"""
        # Implementasi kondisi SELL
        pass
        
    def _wait_conditions(self, analysis):
        """Kondisi untuk WAIT"""
        # Implementasi kondisi WAIT
        pass
