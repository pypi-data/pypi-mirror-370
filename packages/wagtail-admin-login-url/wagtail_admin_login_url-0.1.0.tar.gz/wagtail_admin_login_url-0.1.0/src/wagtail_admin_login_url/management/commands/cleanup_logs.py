# # cron.py or management/commands/cleanup_logs.py

# from datetime import timedelta
# from django.utils.timezone import now
# from wagtail_hide_admin.models import AdminAccessAttempt, Settings


# def cleanup_logs():
#     retention = Settings.load().log_retention_period
#     cutoff = now() - timedelta(days=retention)
#     AdminAccessAttempt.objects.filter(timestamp__lt=cutoff).delete()
