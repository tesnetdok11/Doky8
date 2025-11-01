"""
BRAIN CONTROLLER - Otak utama dengan semua integrasi
"""

import logging
import asyncio
from datetime import datetime

# Core Engines
from core.decision_maker import DecisionMaker
from core.probability_engine import ProbabilityEngine
from core.market_structure_engine import MarketStructureEngine
from core.pattern_recognition import PatternRecognition
from core.adaptive_learner import AdaptiveLearner
from core.multi_tf_synchronizer import MultiTimeframeSynchronizer

# Analytical Engines
from analytical.smc_engine import SMCEngine
from analytical.ict_engine import ICTEngine
from analytical.supply_demand import SupplyDemandEngine
from analytical.volume_analyzer import VolumeAnalyzer
from analytical.price_action import PriceActionEngine
from analytical.trend_engine import TrendEngine
from analytical.historical_pattern_engine import HistoricalPatternEngine

# Integrations
from integrations.binance_api import BinanceAPI
from integrations.okx_api import OKXAPI
from integrations.telegram_ai import TelegramAI
from integrations.github_sync import GitHubSync
from integrations.dns_guard import DNSGuard
from integrations.time_synchronizer import TimeSynchronizer

# DeepSeek AI
from deepseek.deepseek_connector import DeepSeekConnector
from deepseek.deepseek_reasoner import DeepSeekReasoner
from deepseek.deepseek_optimizer import DeepSeekOptimizer
from deepseek.deepseek_memory import DeepSeekMemory

# Data System
from data.market_data import MarketData
from data.historical_data import HistoricalData
from data.signal_logger import SignalLogger
from data.learning_memory import LearningMemory
from data.performance_report import PerformanceReport

# Aggr Data Integration
from integrations.aggr_data_loader import AggrDataLoader
from integrations.aggr_analysis_engine import AggrAnalysisEngine

# Security
from security.watchdog import Watchdog
from security.recovery import RecoverySystem
from security.encryption import EncryptionManager

class BrainController:
    def __init__(self):
        self.setup_components()
        
    def setup_components(self):
        """Setup semua komponen sistem"""
        # Core Analysis
        self.market_data = MarketData()
        self.binance = BinanceAPI()
        self.okx = OKXAPI()
        self.decision_maker = DecisionMaker()
        self.probability_engine = ProbabilityEngine()
        self.market_structure = MarketStructureEngine()
        self.pattern_recognition = PatternRecognition()
        self.adaptive_learner = AdaptiveLearner()
        self.multi_tf_sync = MultiTimeframeSynchronizer()
        
        # Analytical Engines
        self.smc_engine = SMCEngine()
        self.ict_engine = ICTEngine()
        self.supply_demand = SupplyDemandEngine()
        self.volume_analyzer = VolumeAnalyzer()
        self.price_action = PriceActionEngine()
        self.trend_engine = TrendEngine()
        self.historical_pattern = HistoricalPatternEngine()
        
        # DeepSeek AI
        self.deepseek_connector = DeepSeekConnector()
        self.deepseek_reasoner = DeepSeekReasoner()
        self.deepseek_optimizer = DeepSeekOptimizer()
        self.deepseek_memory = DeepSeekMemory()
        
        # Data System
        self.historical_data = HistoricalData()
        self.signal_logger = SignalLogger()
        self.learning_memory = LearningMemory()
        self.performance_report = PerformanceReport()
        
        # Integrations
        self.telegram = TelegramAI()
        self.github_sync = GitHubSync()
        self.dns_guard = DNSGuard()
        self.time_sync = TimeSynchronizer()
        
        # Aggr Data
        self.aggr_loader = AggrDataLoader()
        self.aggr_analyzer = AggrAnalysisEngine()
        
        # Security
        self.watchdog = Watchdog()
        self.recovery = RecoverySystem()
        self.encryption = EncryptionManager()
        
        self.analysis_results = {}
        self.signals = []
        
    async def initialize(self):
        """Initialize semua modul"""
        logging.info("🧠 INITIALIZING BRAIN CONTROLLER...")
        
        try:
            # Initialize Core
            await self.market_data.initialize()
            await self.binance.initialize()
            await self.okx.initialize()
            await self.decision_maker.initialize()
            await self.probability_engine.initialize()
            await self.market_structure.initialize()
            await self.pattern_recognition.initialize()
            await self.adaptive_learner.initialize()
            await self.multi_tf_sync.initialize()
            
            # Initialize Analytical Engines
            await self.smc_engine.initialize()
            await self.ict_engine.initialize()
            await self.supply_demand.initialize()
            await self.volume_analyzer.initialize()
            await self.price_action.initialize()
            await self.trend_engine.initialize()
            await self.historical_pattern.initialize()
            
            # Initialize DeepSeek AI
            await self.deepseek_connector.initialize()
            await self.deepseek_reasoner.initialize(self.deepseek_connector)
            await self.deepseek_optimizer.initialize(self.deepseek_connector)
            await self.deepseek_memory.initialize()
            
            # Initialize Data System
            await self.historical_data.initialize()
            await self.signal_logger.initialize()
            await self.learning_memory.initialize()
            await self.performance_report.initialize(self.learning_memory)
            
            # Initialize Integrations
            await self.telegram.initialize()
            await self.github_sync.initialize()
            await self.dns_guard.initialize()
            await self.time_sync.initialize()
            
            # Initialize Aggr Data
            await self.aggr_loader.initialize()
            await self.aggr_analyzer.initialize(self.aggr_loader)
            
            # Initialize Security
            await self.watchdog.initialize()
            await self.recovery.initialize()
            await self.encryption.initialize()
            
            logging.info("✅ BRAIN CONTROLLER INITIALIZED SUCCESSFULLY")
            
        except Exception as e:
            logging.error(f"❌ Brain controller initialization failed: {e}")
            raise
            
    async def fetch_market_data(self):
        """Fetch market data dari exchanges"""
        try:
            # Coba Binance dulu
            market_data = await self.binance.fetch_market_data()
            if not market_data:
                # Fallback ke OKX
                market_data = await self.okx.fetch_market_data()
                logging.warning("🔄 Using OKX as data backup")
                
            return market_data
            
        except Exception as e:
            logging.error(f"❌ Error fetching market data: {e}")
            return None
            
    async def analyze_market(self, market_data):
        """Lakukan analisis pasar komprehensif dengan Aggr data"""
        if not market_data:
            return None
            
        try:
            analysis = {}
            
            # 1. Sinkronisasi multi timeframe
            tf_data = await self.multi_tf_sync.synchronize(market_data)
            
            # 2. Analisis struktur pasar
            analysis['structure'] = await self.market_structure.analyze(tf_data)
            
            # 3. Recognisi pola
            analysis['patterns'] = await self.pattern_recognition.scan(tf_data)
            
            # 4. Hitung probabilitas
            analysis['probability'] = await self.probability_engine.calculate(
                analysis['structure'], analysis['patterns']
            )
            
            # 5. TAMBAHAN: Analisis dengan Aggr data
            analysis['aggr_enhanced'] = {}
            for pair in list(market_data.keys())[:5]:  # Analyze top 5 pairs
                try:
                    aggr_enhanced = await self.aggr_analyzer.analyze_with_aggr_data(
                        pair, analysis['structure'].get(pair, {}), market_data
                    )
                    analysis['aggr_enhanced'][pair] = aggr_enhanced
                except Exception as e:
                    logging.error(f"❌ Aggr enhancement error for {pair}: {e}")
                    continue
            
            # 6. Adaptive learning
            analysis['learning'] = await self.adaptive_learner.analyze(analysis)
            
            self.analysis_results = analysis
            return analysis
            
        except Exception as e:
            logging.error(f"❌ Market analysis error: {e}")
            return None
            
    async def generate_signals(self, analysis):
        """Generate sinyal trading berdasarkan analisis"""
        if not analysis:
            return []
            
        try:
            signals = await self.decision_maker.generate(analysis)
            
            # Log signals
            for signal in signals:
                logging.info(f"📡 Generated signal: {signal}")
                
            self.signals = signals
            return signals
            
        except Exception as e:
            logging.error(f"❌ Signal generation error: {e}")
            return []
            
    async def update_learning_memory(self, signals):
        """Update memori pembelajaran dengan hasil sinyal"""
        try:
            if signals:
                await self.adaptive_learner.update(signals)
                
        except Exception as e:
            logging.error(f"❌ Learning update error: {e}")
            
    async def cleanup(self):
        """Cleanup semua resources"""
        try:
            await self.binance.cleanup()
            await self.okx.cleanup()
            await self.telegram.cleanup()
            await self.github_sync.cleanup()
            await self.dns_guard.cleanup()
            await self.time_sync.cleanup()
            await self.aggr_loader.cleanup()
            await self.aggr_analyzer.cleanup()
            await self.deepseek_connector.cleanup()
            await self.deepseek_memory.cleanup()
            await self.historical_data.cleanup()
            await self.signal_logger.cleanup()
            await self.learning_memory.cleanup()
            await self.performance_report.cleanup()
            await self.encryption.cleanup()
            
            logging.info("🔒 Brain controller cleanup completed")
            
        except Exception as e:
            logging.error(f"❌ Brain controller cleanup error: {e}")
