from celery import Celery, Task
from celery.schedules import crontab
from app import app

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
    include=["tasks"],
)


class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery_app.Task = FlaskTask

celery_app.conf.timezone = "Asia/Kolkata"
celery_app.conf.enable_utc = False

celery_app.conf.beat_schedule = {
    "daily-reminders": {
        "task": "tasks.daily_reminders",
        "schedule": crontab(hour=7, minute=0),
    },
    "monthly-reports": {
        "task": "tasks.monthly_reports",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),
    },
}
