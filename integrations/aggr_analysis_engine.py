"""
AGGR ANALYSIS ENGINE - Engine analisis khusus untuk data aggregated trades
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AggrAnalysisEngine:
    def __init__(self):
        self.aggr_loader = None
        
    async def initialize(self, aggr_loader):
        """Initialize Aggr analysis engine"""
        logging.info("🔍 INITIALIZING AGGR ANALYSIS ENGINE...")
        self.aggr_loader = aggr_loader
        
    async def analyze_with_aggr_data(self, pair, technical_analysis, market_data):
        """Enhance technical analysis with aggregated trade data"""
        try:
            # Get recent aggregated data
            aggr_data = await self.aggr_loader.get_recent_aggr_data(pair, days_back=3)
            
            if not aggr_data:
                logging.warning(f"⚠️ No aggr data available for {pair}")
                return technical_analysis
                
            # Perform aggr-specific analysis
            aggr_analysis = {
                'market_depth': await self.aggr_loader.analyze_market_depth(aggr_data),
                'large_orders': await self.aggr_loader.detect_large_orders(aggr_data),
                'volume_profile': await self._analyze_volume_profile(aggr_data),
                'trade_flow': await self._analyze_trade_flow(aggr_data),
                'liquidity_analysis': await self._analyze_liquidity(aggr_data)
            }
            
            # Enhance technical analysis with aggr insights
            enhanced_analysis = await self._enhance_technical_analysis(
                technical_analysis, aggr_analysis, market_data
            )
            
            return enhanced_analysis
            
        except Exception as e:
            logging.error(f"❌ Aggr analysis error for {pair}: {e}")
            return technical_analysis
            
    async def _analyze_volume_profile(self, aggr_data):
        """Analyze volume profile from aggregated data"""
        try:
            df = pd.DataFrame(aggr_data['data'])
            
            # Create volume profile (price levels with volume)
            price_precision = 0.01  # Adjust based on asset
            df['price_level'] = (df['price'] / price_precision).round() * price_precision
            
            volume_profile = df.groupby('price_level').agg({
                'volume': 'sum',
                'trade_intensity': 'mean'
            }).reset_index()
            
            volume_profile = volume_profile.sort_values('volume', ascending=False)
            
            # Find POC (Point of Control)
            poc = volume_profile.iloc[0] if not volume_profile.empty else None
            
            # Value Area (70% of volume)
            total_volume = volume_profile['volume'].sum()
            volume_profile['cumulative_volume'] = volume_profile['volume'].cumsum()
            value_area = volume_profile[volume_profile['cumulative_volume'] <= total_volume * 0.7]
            
            return {
                'poc': poc.to_dict() if poc is not None else None,
                'value_area_high': value_area['price_level'].max() if not value_area.empty else None,
                'value_area_low': value_area['price_level'].min() if not value_area.empty else None,
                'volume_distribution': volume_profile.to_dict('records')[:20]  # Top 20 levels
            }
            
        except Exception as e:
            logging.error(f"❌ Volume profile analysis error: {e}")
            return {}
            
    async def _analyze_trade_flow(self, aggr_data):
        """Analyze trade flow and order imbalance"""
        try:
            df = pd.DataFrame(aggr_data['data'])
            
            if 'estimated_side' not in df.columns:
                # Estimate sides based on price movement
                df['price_change'] = df['price'].pct_change()
                df['estimated_side'] = np.where(df['price_change'] > 0, 'buy', 'sell')
                
            # Calculate buy/sell volume
            buy_volume = df[df['estimated_side'] == 'buy']['volume'].sum()
            sell_volume = df[df['estimated_side'] == 'sell']['volume'].sum()
            
            # Order imbalance
            total_volume = buy_volume + sell_volume
            order_imbalance = (buy_volume - sell_volume) / total_volume if total_volume > 0 else 0
            
            # Cumulative delta
            df['delta'] = np.where(df['estimated_side'] == 'buy', df['volume'], -df['volume'])
            df['cumulative_delta'] = df['delta'].cumsum()
            
            return {
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'order_imbalance': order_imbalance,
                'net_volume': buy_volume - sell_volume,
                'cumulative_delta': df['cumulative_delta'].iloc[-1] if not df.empty else 0,
                'dominant_side': 'buy' if order_imbalance > 0 else 'sell'
            }
            
        except Exception as e:
            logging.error(f"❌ Trade flow analysis error: {e}")
            return {}
            
    async def _analyze_liquidity(self, aggr_data):
        """Analyze liquidity conditions from aggregated data"""
        try:
            df = pd.DataFrame(aggr_data['data'])
            
            # Calculate liquidity metrics
            volume_volatility = df['volume'].std() / df['volume'].mean()
            trade_size_variance = df['volume'].var()
            
            # Liquidity clusters (areas with high trading activity)
            time_buckets = pd.cut(pd.to_datetime(df['timestamp']).dt.hour, bins=6)
            liquidity_by_hour = df.groupby(time_buckets)['volume'].sum()
            
            # Market efficiency (how quickly large trades are absorbed)
            large_trades = df[df['volume'] > df['volume'].quantile(0.9)]
            price_impact = large_trades['price_change_abs'].mean() if not large_trades.empty else 0
            
            return {
                'volume_volatility': volume_volatility,
                'trade_size_variance': trade_size_variance,
                'liquidity_clusters': liquidity_by_hour.to_dict(),
                'price_impact_large_trades': price_impact,
                'liquidity_score': await self._calculate_liquidity_score(volume_volatility, price_impact)
            }
            
        except Exception as e:
            logging.error(f"❌ Liquidity analysis error: {e}")
            return {}
            
    async def _calculate_liquidity_score(self, volume_volatility, price_impact):
        """Calculate overall liquidity score"""
        try:
            # Lower volatility and lower price impact = better liquidity
            volatility_score = max(0, 1 - min(volume_volatility, 2) / 2)  # Normalize to 0-1
            impact_score = max(0, 1 - min(abs(price_impact) * 100, 1))  # Normalize to 0-1
            
            liquidity_score = (volatility_score * 0.6 + impact_score * 0.4) * 100
            return min(100, max(0, liquidity_score))
            
        except:
            return 50  # Default score
            
    async def _enhance_technical_analysis(self, technical_analysis, aggr_analysis, market_data):
        """Enhance technical analysis with aggregated data insights"""
        try:
            enhanced = technical_analysis.copy()
            
            # Add aggr analysis results
            enhanced['aggr_analysis'] = aggr_analysis
            
            # Enhance confidence based on aggr data
            base_confidence = enhanced.get('confidence', 0.5)
            aggr_boost = await self._calculate_aggr_confidence_boost(aggr_analysis)
            
            enhanced['confidence'] = min(0.95, base_confidence + aggr_boost)
            enhanced['aggr_confidence_boost'] = aggr_boost
            
            # Enhance signals with liquidity context
            if 'signals' in enhanced:
                enhanced['signals'] = await self._enhance_signals_with_liquidity(
                    enhanced['signals'], aggr_analysis
                )
                
            return enhanced
            
        except Exception as e:
            logging.error(f"❌ Technical analysis enhancement error: {e}")
            return technical_analysis
            
    async def _calculate_aggr_confidence_boost(self, aggr_analysis):
        """Calculate confidence boost from aggregated data analysis"""
        try:
            boost = 0.0
            
            # Boost from order imbalance confirmation
            trade_flow = aggr_analysis.get('trade_flow', {})
            order_imbalance = trade_flow.get('order_imbalance', 0)
            
            if abs(order_imbalance) > 0.3:  # Strong imbalance
                boost += 0.05
                
            # Boost from liquidity score
            liquidity = aggr_analysis.get('liquidity_analysis', {})
            liquidity_score = liquidity.get('liquidity_score', 50)
            
            if liquidity_score > 70:  # Good liquidity
                boost += 0.03
                
            # Boost from clear volume profile
            volume_profile = aggr_analysis.get('volume_profile', {})
            if volume_profile.get('poc') and volume_profile.get('value_area_high'):
                boost += 0.02
                
            return min(boost, 0.1)  # Max 10% boost
            
        except:
            return 0.0
            
    async def _enhance_signals_with_liquidity(self, signals, aggr_analysis):
        """Enhance trading signals with liquidity context"""
        try:
            enhanced_signals = []
            
            for signal in signals:
                enhanced_signal = signal.copy()
                
                # Add liquidity context to signal
                liquidity = aggr_analysis.get('liquidity_analysis', {})
                enhanced_signal['liquidity_score'] = liquidity.get('liquidity_score', 50)
                enhanced_signal['liquidity_context'] = self._get_liquidity_context(
                    liquidity.get('liquidity_score', 50)
                )
                
                # Add volume profile context
                volume_profile = aggr_analysis.get('volume_profile', {})
                enhanced_signal['volume_profile'] = {
                    'poc_price': volume_profile.get('poc', {}).get('price_level'),
                    'value_area_high': volume_profile.get('value_area_high'),
                    'value_area_low': volume_profile.get('value_area_low')
                }
                
                enhanced_signals.append(enhanced_signal)
                
            return enhanced_signals
            
        except Exception as e:
            logging.error(f"❌ Signal enhancement error: {e}")
            return signals
            
    def _get_liquidity_context(self, liquidity_score):
        """Get liquidity context description"""
        if liquidity_score >= 80:
            return "excellent_liquidity"
        elif liquidity_score >= 60:
            return "good_liquidity" 
        elif liquidity_score >= 40:
            return "moderate_liquidity"
        else:
            return "poor_liquidity"
            
    async def detect_institutional_activity(self, aggr_data):
        """Detect potential institutional trading activity"""
        try:
            if not aggr_data or not aggr_data['data']:
                return []
                
            df = pd.DataFrame(aggr_data['data'])
            
            # Look for patterns indicative of institutional activity
            large_orders = await self.aggr_loader.detect_large_orders(aggr_data, threshold_ratio=10)
            institutional_signs = []
            
            for order in large_orders:
                # Institutional orders often have specific characteristics
                if (order['size_ratio'] > 20 and 
                    order['significance'] == 'high'):
                    
                    institutional_signs.append({
                        'timestamp': order['timestamp'],
                        'type': 'large_block_trade',
                        'size_ratio': order['size_ratio'],
                        'estimated_side': order['estimated_side'],
                        'confidence': 'high' if order['size_ratio'] > 50 else 'medium'
                    })
                    
            # Look for order splitting (multiple large orders in short time)
            df_sorted = df.sort_values('timestamp')
            df_sorted['time_diff'] = df_sorted['timestamp'].diff().dt.total_seconds()
            
            # Cluster large trades close in time
            large_trades_mask = df_sorted['volume'] > df_sorted['volume'].quantile(0.95)
            clustered_large_trades = df_sorted[large_trades_mask & (df_sorted['time_diff'] < 300)]  # 5 minutes
            
            if len(clustered_large_trades) >= 3:
                total_cluster_volume = clustered_large_trades['volume'].sum()
                avg_trade_size = df_sorted['volume'].mean()
                
                if total_cluster_volume > avg_trade_size * 100:
                    institutional_signs.append({
                        'timestamp': clustered_large_trades['timestamp'].iloc[-1],
                        'type': 'order_splitting_cluster',
                        'total_volume': total_cluster_volume,
                        'trade_count': len(clustered_large_trades),
                        'time_span_seconds': (clustered_large_trades['timestamp'].iloc[-1] - 
                                            clustered_large_trades['timestamp'].iloc[0]).total_seconds(),
                        'confidence': 'high'
                    })
                    
            return institutional_signs
            
        except Exception as e:
            logging.error(f"❌ Institutional activity detection error: {e}")
            return []
            
    async def cleanup(self):
        """Cleanup Aggr analysis engine"""
        logging.info("🔒 Aggr analysis engine cleanup completed")
