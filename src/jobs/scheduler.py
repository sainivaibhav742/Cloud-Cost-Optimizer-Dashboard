from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from src.jobs.daily_cost_fetch import fetch_and_store_daily_costs
from src.services.anomaly_detection import AnomalyDetector
from src.models.database import get_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_for_anomalies():
    """
    Job to check for cost anomalies and send alerts.
    """
    logger.info(f"[{datetime.now()}] Checking for cost anomalies...")

    try:
        from src.services.alert_service import AlertService

        db = next(get_db())
        detector = AnomalyDetector(db)
        recommendations = detector.get_all_recommendations()

        total_alerts = sum(len(recs) for recs in recommendations.values())

        if total_alerts > 0:
            logger.warning(f"Found {total_alerts} cost optimization opportunities:")
            for category, recs in recommendations.items():
                if recs:
                    logger.warning(f"  {category.upper()}: {len(recs)} issues")
                    for rec in recs[:3]:  # Log first 3 per category
                        logger.warning(f"    - {rec.get('suggestion', 'Check service')}")

            # Send alerts
            alert_service = AlertService()
            alert_service.send_anomaly_alerts(recommendations)
        else:
            logger.info("No anomalies detected")

    except Exception as e:
        logger.error(f"Error in anomaly check job: {e}")

def setup_scheduler():
    """
    Set up the APScheduler for automated jobs.
    """
    scheduler = BackgroundScheduler()

    # Daily cost fetch at 2 AM
    scheduler.add_job(
        fetch_and_store_daily_costs,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_cost_fetch',
        name='Daily Cost Data Fetch',
        replace_existing=True
    )

    # Daily anomaly check at 3 AM
    scheduler.add_job(
        check_for_anomalies,
        trigger=CronTrigger(hour=3, minute=0),
        id='anomaly_check',
        name='Daily Anomaly Check',
        replace_existing=True
    )

    logger.info("Scheduler configured with daily jobs")
    return scheduler

def start_scheduler():
    """
    Start the scheduler.
    """
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started")

    try:
        # Keep the scheduler running
        import time
        while True:
            time.sleep(60)  # Check every minute
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    start_scheduler()
