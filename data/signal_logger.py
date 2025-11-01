"""
SIGNAL LOGGER - Pencatatan sinyal & hasil analisa
"""

import logging
import json
import csv
import asyncio
from datetime import datetime
from pathlib import Path

class SignalLogger:
    def __init__(self):
        self.log_dir = "logs/signals"
        self.current_day = None
        self.csv_writer = None
        self.csv_file = None
        
    async def initialize(self):
        """Initialize signal logger"""
        logging.info("📝 INITIALIZING SIGNAL LOGGER...")
        
        try:
            Path(self.log_dir).mkdir(parents=True, exist_ok=True)
            await self._setup_daily_logging()
            logging.info("✅ SIGNAL LOGGER INITIALIZED")
            
        except Exception as e:
            logging.error(f"❌ Signal logger initialization failed: {e}")
            
    async def _setup_daily_logging(self):
        """Setup daily CSV logging"""
        try:
            today = datetime.utcnow().strftime('%Y-%m-%d')
            
            if self.current_day != today:
                # Close previous file if exists
                if self.csv_file:
                    self.csv_file.close()
                    
                # Create new CSV file for today
                filename = f"{self.log_dir}/signals_{today}.csv"
                file_exists = Path(filename).exists()
                
                self.csv_file = open(filename, 'a', newline='', encoding='utf-8')
                self.csv_writer = csv.writer(self.csv_file)
                
                # Write header if new file
                if not file_exists:
                    self.csv_writer.writerow([
                        'timestamp', 'signal_id', 'pair', 'direction', 'entry_price',
                        'stop_loss', 'take_profit', 'confidence', 'adjusted_confidence',
                        'timeframe', 'reason', 'analysis_data', 'ai_optimized'
                    ])
                    
                self.current_day = today
                logging.info(f"📁 New signal log created: {filename}")
                
        except Exception as e:
            logging.error(f"❌ Daily logging setup error: {e}")
            
    async def log_signal(self, signal):
        """Log trading signal"""
        try:
            await self._setup_daily_logging()  # Ensure we're using current day's file
            
            signal_id = signal.get('signal_id', 
                                 f"sig_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
            
            # Prepare data for CSV
            csv_row = [
                datetime.utcnow().isoformat(),
                signal_id,
                signal.get('pair', ''),
                signal.get('direction', ''),
                signal.get('entry', 0),
                signal.get('stop_loss', 0),
                signal.get('take_profit', 0),
                signal.get('confidence', 0),
                signal.get('adjusted_confidence', signal.get('confidence', 0)),
                signal.get('timeframe', '15m'),
                signal.get('reason', ''),
                json.dumps(signal.get('analysis_data', {}), default=str),
                signal.get('ai_optimized', False)
            ]
            
            # Write to CSV
            self.csv_writer.writerow(csv_row)
            self.csv_file.flush()
            
            # Also write to JSON for detailed analysis
            await self._log_signal_json(signal, signal_id)
            
            logging.info(f"📋 Signal logged: {signal_id} - {signal.get('pair')} {signal.get('direction')}")
            
        except Exception as e:
            logging.error(f"❌ Signal logging error: {e}")
            
    async def _log_signal_json(self, signal, signal_id):
        """Log signal in JSON format for detailed analysis"""
        try:
            json_log = {
                'signal_id': signal_id,
                'timestamp': datetime.utcnow().isoformat(),
                'signal_data': signal,
                'metadata': {
                    'log_version': '1.0',
                    'system': 'DokyOS',
                    'environment': 'production'
                }
            }
            
            filename = f"{self.log_dir}/detailed_{signal_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_log, f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"❌ JSON signal logging error: {e}")
            
    async def log_signal_outcome(self, signal_id, outcome, actual_pnl=None, notes=""):
        """Log signal outcome (result)"""
        try:
            outcome_data = {
                'signal_id': signal_id,
                'outcome': outcome,  # 'success', 'failure', 'partial', 'cancelled'
                'actual_pnl': actual_pnl,
                'notes': notes,
                'outcome_timestamp': datetime.utcnow().isoformat()
            }
            
            # Append to outcomes file
            outcomes_file = f"{self.log_dir}/signal_outcomes.jsonl"
            with open(outcomes_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(outcome_data) + '\n')
                
            # Update CSV if possible (find signal and update)
            await self._update_csv_outcome(signal_id, outcome, actual_pnl)
            
            logging.info(f"📋 Outcome logged for {signal_id}: {outcome}")
            
        except Exception as e:
            logging.error(f"❌ Outcome logging error: {e}")
            
    async def _update_csv_outcome(self, signal_id, outcome, actual_pnl):
        """Update CSV with outcome data"""
        try:
            # This would require reading the CSV, finding the signal, and updating it
            # For simplicity, we'll just log to separate files
            pass
            
        except Exception as e:
            logging.error(f"❌ CSV outcome update error: {e}")
            
    async def get_recent_signals(self, hours=24, pair=None):
        """Get recent signals"""
        try:
            signals = []
            start_time = datetime.utcnow().timestamp() - (hours * 3600)
            
            # Read from today's CSV
            today_file = f"{self.log_dir}/signals_{datetime.utcnow().strftime('%Y-%m-%d')}.csv"
            if Path(today_file).exists():
                with open(today_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        row_time = datetime.fromisoformat(row['timestamp']).timestamp()
                        if row_time >= start_time:
                            if pair is None or row['pair'] == pair:
                                signals.append(row)
                                
            return signals
            
        except Exception as e:
            logging.error(f"❌ Recent signals query error: {e}")
            return []
            
    async def get_signal_statistics(self, days=7):
        """Get signal statistics"""
        try:
            stats = {
                'total_signals': 0,
                'successful_signals': 0,
                'failed_signals': 0,
                'total_pnl': 0.0,
                'accuracy_rate': 0.0,
                'average_confidence': 0.0,
                'by_pair': {},
                'by_direction': {'BUY': 0, 'SELL': 0}
            }
            
            # Read outcomes
            outcomes_file = f"{self.log_dir}/signal_outcomes.jsonl"
            if Path(outcomes_file).exists():
                with open(outcomes_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        outcome_data = json.loads(line.strip())
                        signal_id = outcome_data['signal_id']
                        outcome = outcome_data['outcome']
                        pnl = outcome_data.get('actual_pnl', 0)
                        
                        # Check if within time range
                        outcome_time = datetime.fromisoformat(outcome_data['outcome_timestamp'])
                        if (datetime.utcnow() - outcome_time).days <= days:
                            stats['total_signals'] += 1
                            
                            if outcome == 'success':
                                stats['successful_signals'] += 1
                                stats['total_pnl'] += pnl
                            elif outcome == 'failure':
                                stats['failed_signals'] += 1
                                stats['total_pnl'] += pnl
                                
            # Calculate accuracy
            if stats['total_signals'] > 0:
                stats['accuracy_rate'] = stats['successful_signals'] / stats['total_signals']
                
            return stats
            
        except Exception as e:
            logging.error(f"❌ Signal statistics error: {e}")
            return {}
            
    async def export_signals_report(self, start_date, end_date, format='json'):
        """Export signals report for given period"""
        try:
            report = {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'generated_at': datetime.utcnow().isoformat(),
                'signals': [],
                'statistics': {}
            }
            
            # Collect signals from CSV files in date range
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                csv_file = f"{self.log_dir}/signals_{date_str}.csv"
                
                if Path(csv_file).exists():
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            signal_time = datetime.fromisoformat(row['timestamp'])
                            if start_date <= signal_time <= end_date:
                                report['signals'].append(row)
                                
                current_date += timedelta(days=1)
                
            # Calculate statistics
            if report['signals']:
                report['statistics'] = await self._calculate_period_statistics(report['signals'])
                
            # Export in requested format
            if format == 'json':
                output_file = f"logs/exports/signals_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                Path("logs/exports").mkdir(exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, default=str)
                    
            elif format == 'csv':
                output_file = f"logs/exports/signals_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                await self._export_csv_report(report, output_file)
                
            logging.info(f"📊 Signals report exported: {output_file}")
            return output_file
            
        except Exception as e:
            logging.error(f"❌ Signals report export error: {e}")
            return None
            
    async def _calculate_period_statistics(self, signals):
        """Calculate statistics for signal period"""
        stats = {
            'total_count': len(signals),
            'buy_count': len([s for s in signals if s['direction'] == 'BUY']),
            'sell_count': len([s for s in signals if s['direction'] == 'SELL']),
            'average_confidence': 0.0,
            'high_confidence_count': 0,
            'by_pair': {},
            'by_timeframe': {}
        }
        
        if signals:
            confidences = [float(s.get('adjusted_confidence', s.get('confidence', 0))) for s in signals]
            stats['average_confidence'] = sum(confidences) / len(confidences)
            stats['high_confidence_count'] = len([c for c in confidences if c >= 0.8])
            
            # Count by pair
            for signal in signals:
                pair = signal['pair']
                stats['by_pair'][pair] = stats['by_pair'].get(pair, 0) + 1
                
            # Count by timeframe
            for signal in signals:
                tf = signal['timeframe']
                stats['by_timeframe'][tf] = stats['by_timeframe'].get(tf, 0) + 1
                
        return stats
        
    async def _export_csv_report(self, report, output_file):
        """Export report as CSV"""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Signal ID', 'Timestamp', 'Pair', 'Direction', 'Entry Price',
                    'Stop Loss', 'Take Profit', 'Confidence', 'Timeframe', 'Reason'
                ])
                
                # Write data
                for signal in report['signals']:
                    writer.writerow([
                        signal.get('signal_id', ''),
                        signal.get('timestamp', ''),
                        signal.get('pair', ''),
                        signal.get('direction', ''),
                        signal.get('entry_price', ''),
                        signal.get('stop_loss', ''),
                        signal.get('take_profit', ''),
                        signal.get('confidence', ''),
                        signal.get('timeframe', ''),
                        signal.get('reason', '')[:100]  # Truncate long reasons
                    ])
                    
        except Exception as e:
            logging.error(f"❌ CSV export error: {e}")
            
    async def cleanup_old_logs(self, days_to_keep=30):
        """Cleanup old log files"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for log_file in Path(self.log_dir).glob("*.csv"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    deleted_count += 1
                    
            logging.info(f"🧹 Cleaned up {deleted_count} old log files")
            
        except Exception as e:
            logging.error(f"❌ Log cleanup error: {e}")
            
    async def cleanup(self):
        """Cleanup signal logger"""
        if self.csv_file:
            self.csv_file.close()
        logging.info("🔒 Signal logger cleanup completed")
