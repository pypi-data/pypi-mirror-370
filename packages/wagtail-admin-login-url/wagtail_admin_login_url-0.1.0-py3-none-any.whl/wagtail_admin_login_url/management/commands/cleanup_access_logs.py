from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from wagtail_hide_admin.models import AccessReport, Settings


class Command(BaseCommand):
    help = "Deletes old access logs based on retention policy."

    def handle(self, *args, **kwargs):
        settings = Settings.load()
        retention_days = settings.log_retention_period
        threshold = now() - timedelta(days=retention_days)

        deleted, _ = AccessReport.objects.filter(timestamp__lt=threshold).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} access log(s)."))

    # help = "Delete AccessReport entries older than the configured retention period"

    # def handle(self, *args, **options):
    #     settings = Settings.load()
    #     days = settings.log_retention_period
    #     threshold_date = now() - timedelta(days=days)

    #     old_logs = AccessReport.objects.filter(timestamp__lt=threshold_date)
    #     count = old_logs.count()
    #     old_logs.delete()

    #     self.stdout.write(self.style.SUCCESS(f"Deleted {count} old access log(s) older than {days} days."))


# Schedule It (Cron or Task Scheduler)
# 0 0 * * * /path/to/your/venv/bin/python manage.py cleanup_access_logs

# Or if you're using Celery Beat
# from celery.schedules import crontab

# CELERY_BEAT_SCHEDULE = {
#     'cleanup-access-logs': {
#         'task': 'wagtail_hide_admin.tasks.cleanup_access_logs',
#         'schedule': crontab(minute=0, hour=0),  # every midnight
#     },
# }
