import logging
from datetime import datetime, timezone

import os, sys, uuid, requests
sys.path.append(os.getcwd())
from App.Controllers.API.IoTController import perform_prediction_and_store

from apscheduler.schedulers.background import BackgroundScheduler

# Buat logger
logging.basicConfig(level=logging.INFO)

def init_scheduler():
    logging.info("Initializing AI Scheduler...")
    """Mulai scheduler hanya sekali saat Flask start"""
    try:
        start_scheduler()
        logging.info("AI Scheduler started successfully.")
    except Exception as e:
        logging.error(f"Failed to start AI Scheduler: {e}", exc_info=True)


def job():
    """Job yang akan dipanggil jam 02:00 dan 09:00 UTC"""
    today_date_utc = datetime.now(timezone.utc).date()
    logging.info(f"Running perform_prediction_and_store for {today_date_utc} (UTC)")
    
    try:
        result = perform_prediction_and_store(today_date_utc)
        logging.info(f"Prediction job completed for {today_date_utc}, result={result}")
    except Exception as e:
        logging.error(f"Error running prediction for {today_date_utc}: {e}", exc_info=True)

def start_scheduler():
    """Inisialisasi dan mulai scheduler"""
    scheduler = BackgroundScheduler(timezone="UTC")
    # Jadwal: setiap jam 02:00 dan 09:00 UTC
    # scheduler.add_job(job, 'cron', hour='2,9', minute='00')
    scheduler.add_job(job, 'cron', hour='2,7', minute='35')
    scheduler.start()
    logging.info("APScheduler started: will run at 02:00 and 09:00 UTC daily.")

