"""
Automated Scheduler
Runs daily evaluation, retraining, and data updates
"""

import os
import sys
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_engine import LearningEngine
from database import get_db, Prediction
from multi_source_data_fetcher import MultiSourceDataFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingScheduler:
    """
    Automated scheduler for trading system tasks
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.learning_engine = LearningEngine()
        self.data_fetcher = MultiSourceDataFetcher()
    
    def setup_jobs(self):
        """
        Setup all scheduled jobs
        """
        # Daily evaluation at 6 PM IST
        self.scheduler.add_job(
            self.daily_evaluation,
            CronTrigger(hour=18, minute=0, timezone='Asia/Kolkata'),
            id='daily_evaluation',
            name='Daily Prediction Evaluation',
            replace_existing=True
        )
        
        # Weekly retraining on Sunday at 8 PM IST
        self.scheduler.add_job(
            self.weekly_retraining,
            CronTrigger(day_of_week='sun', hour=20, minute=0, timezone='Asia/Kolkata'),
            id='weekly_retraining',
            name='Weekly Model Retraining',
            replace_existing=True
        )
        
        # Daily data refresh at 9:30 AM IST (market open)
        self.scheduler.add_job(
            self.market_open_refresh,
            CronTrigger(hour=9, minute=30, timezone='Asia/Kolkata'),
            id='market_open_refresh',
            name='Market Open Data Refresh',
            replace_existing=True
        )
        
        # End of day data update at 3:45 PM IST (market close)
        self.scheduler.add_job(
            self.market_close_update,
            CronTrigger(hour=15, minute=45, timezone='Asia/Kolkata'),
            id='market_close_update',
            name='Market Close Data Update',
            replace_existing=True
        )
        
        # Hourly cache cleanup
        self.scheduler.add_job(
            self.cache_cleanup,
            CronTrigger(minute=0, timezone='Asia/Kolkata'),
            id='cache_cleanup',
            name='Hourly Cache Cleanup',
            replace_existing=True
        )
        
        logger.info("All scheduled jobs configured")
    
    def daily_evaluation(self):
        """
        Evaluate predictions daily (runs at 6 PM)
        """
        logger.info("="*60)
        logger.info("DAILY EVALUATION STARTED")
        logger.info("="*60)
        
        try:
            # Evaluate predictions that are 30+ days old
            results = self.learning_engine.evaluate_predictions(min_days=30)
            
            logger.info(f"Evaluated {results['evaluated_count']} predictions")
            logger.info(f"Overall accuracy: {results['overall_accuracy']:.1f}%")
            
            # Log agent performance
            for agent, acc in results['agent_accuracy'].items():
                logger.info(f"  {agent}: {acc:.1f}%")
            
            # Trigger retraining if accuracy dropped
            if results['overall_accuracy'] < 65:
                logger.warning("Accuracy below threshold, triggering retraining")
                self.weekly_retraining()
            
            logger.info("Daily evaluation completed successfully")
            
        except Exception as e:
            logger.error(f"Daily evaluation failed: {e}", exc_info=True)
    
    def weekly_retraining(self):
        """
        Retrain models weekly (runs on Sunday 8 PM)
        """
        logger.info("="*60)
        logger.info("WEEKLY RETRAINING STARTED")
        logger.info("="*60)
        
        try:
            # Get agent accuracy
            with get_db() as session:
                predictions = session.query(Prediction).filter(
                    Prediction.evaluated == True
                ).all()
                
                if len(predictions) < 10:
                    logger.warning("Not enough evaluated predictions for retraining")
                    return
            
            # Calculate agent accuracy
            agent_accuracy = self._calculate_agent_accuracy(predictions)
            
            # Optimize weights
            new_weights = self.learning_engine.optimize_weights(agent_accuracy)
            
            logger.info("New agent weights:")
            for agent, weight in new_weights.items():
                logger.info(f"  {agent}: {weight:.3f}")
            
            logger.info("Weekly retraining completed successfully")
            
        except Exception as e:
            logger.error(f"Weekly retraining failed: {e}", exc_info=True)
    
    def market_open_refresh(self):
        """
        Refresh data at market open (9:30 AM)
        """
        logger.info("Market open - refreshing watchlist data")
        
        try:
            # Get active tickers from predictions
            with get_db() as session:
                recent_predictions = session.query(Prediction.ticker).filter(
                    Prediction.evaluated == False
                ).distinct().all()
                
                tickers = [p.ticker for p in recent_predictions]
            
            # Refresh data for each ticker
            for ticker in tickers[:50]:  # Limit to 50 to avoid rate limits
                try:
                    data = self.data_fetcher.fetch_stock_data(ticker, period="1mo")
                    if data:
                        logger.info(f"✅ Refreshed {ticker}: ₹{data['current_price']:.2f}")
                except Exception as e:
                    logger.error(f"Failed to refresh {ticker}: {e}")
            
            logger.info("Market open refresh completed")
            
        except Exception as e:
            logger.error(f"Market open refresh failed: {e}", exc_info=True)
    
    def market_close_update(self):
        """
        Update data at market close (3:45 PM)
        """
        logger.info("Market close - updating end of day data")
        
        try:
            # Similar to market_open_refresh but with full day data
            with get_db() as session:
                recent_predictions = session.query(Prediction.ticker).filter(
                    Prediction.evaluated == False
                ).distinct().all()
                
                tickers = [p.ticker for p in recent_predictions]
            
            updated_count = 0
            for ticker in tickers:
                try:
                    data = self.data_fetcher.fetch_stock_data(ticker, period="1mo")
                    if data:
                        updated_count += 1
                except Exception as e:
                    logger.error(f"Failed to update {ticker}: {e}")
            
            logger.info(f"Market close update completed: {updated_count} tickers updated")
            
        except Exception as e:
            logger.error(f"Market close update failed: {e}", exc_info=True)
    
    def cache_cleanup(self):
        """
        Clean up expired cache entries (runs hourly)
        """
        logger.info("Running cache cleanup")
        
        try:
            from database import StockData
            
            with get_db() as session:
                # Delete expired cache entries
                deleted = session.query(StockData).filter(
                    StockData.expires_at < datetime.now()
                ).delete()
                
                session.commit()
                
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} expired cache entries")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}", exc_info=True)
    
    def _calculate_agent_accuracy(self, predictions: list) -> dict:
        """
        Calculate accuracy for each agent
        """
        agent_stats = {
            'technical': {'correct': 0, 'total': 0},
            'fundamental': {'correct': 0, 'total': 0},
            'risk': {'correct': 0, 'total': 0},
            'market_context': {'correct': 0, 'total': 0}
        }
        
        for pred in predictions:
            if pred.agent_evaluation:
                for agent, result in pred.agent_evaluation.items():
                    if agent in agent_stats:
                        agent_stats[agent]['total'] += 1
                        if result == 'right':
                            agent_stats[agent]['correct'] += 1
        
        # Calculate accuracy rates
        accuracy = {}
        for agent, stats in agent_stats.items():
            if stats['total'] > 0:
                accuracy[agent] = (stats['correct'] / stats['total']) * 100
            else:
                accuracy[agent] = 50.0  # Default
        
        return accuracy
    
    def start(self):
        """
        Start the scheduler
        """
        self.setup_jobs()
        self.scheduler.start()
        logger.info("Scheduler started successfully")
        logger.info("Scheduled jobs:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name} (next run: {job.next_run_time})")
    
    def stop(self):
        """
        Stop the scheduler
        """
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def run_job_now(self, job_id: str):
        """
        Run a specific job immediately
        """
        job = self.scheduler.get_job(job_id)
        if job:
            logger.info(f"Running job: {job.name}")
            job.func()
        else:
            logger.error(f"Job not found: {job_id}")


if __name__ == "__main__":
    # Run scheduler
    scheduler = TradingScheduler()
    
    print("\n🤖 AUTOMATED TRADING SCHEDULER")
    print("="*60)
    print("\nScheduled Jobs:")
    print("  1. Daily Evaluation - 6:00 PM IST")
    print("  2. Weekly Retraining - Sunday 8:00 PM IST")
    print("  3. Market Open Refresh - 9:30 AM IST")
    print("  4. Market Close Update - 3:45 PM IST")
    print("  5. Cache Cleanup - Every hour")
    print("\n" + "="*60)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-now', choices=['evaluation', 'retraining', 'refresh', 'update', 'cleanup'],
                       help='Run a job immediately')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    if args.run_now:
        # Run specific job immediately
        job_map = {
            'evaluation': 'daily_evaluation',
            'retraining': 'weekly_retraining',
            'refresh': 'market_open_refresh',
            'update': 'market_close_update',
            'cleanup': 'cache_cleanup'
        }
        
        scheduler.setup_jobs()
        scheduler.run_job_now(job_map[args.run_now])
        
    elif args.daemon:
        # Run as daemon
        scheduler.start()
        print("\n✅ Scheduler running in background")
        print("Press Ctrl+C to stop\n")
        
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
            scheduler.stop()
            print("✅ Scheduler stopped")
    
    else:
        # Show help
        parser.print_help()
