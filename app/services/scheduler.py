from apscheduler.schedulers.background import BackgroundScheduler
from app.services.firebase import firebase_service
import datetime

scheduler = BackgroundScheduler()

def check_deadlines():
    """
    Checks for tasks that are due soon and sends reminders.
    """
    print(f"[{datetime.datetime.now()}] Checking deadlines...")
    tasks = firebase_service.get_tasks()
    for task in tasks:
        deadline = task.get('deadline')
        status = task.get('status')
        if deadline and status != 'completed':
            # Logic to compare dates would go here
            # For demo purposes, we just print
            print(f"Reminder: Task '{task.get('title')}' is due on {deadline}.")

def start_scheduler():
    scheduler.add_job(check_deadlines, 'interval', minutes=1) # Check every minute for demo
    scheduler.start()
    print("Scheduler started.")
