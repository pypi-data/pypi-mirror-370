from django.http import HttpRequest

from .models import AccessReport
from .models import Settings as AdminSettings
from .utils import get_client_ip


def log_access(*, request: HttpRequest, success: bool, reason: str = ''):

    settings = AdminSettings.load()
    if not settings.logging_enabled:
        return

    should_log = False
    if settings.log_types == settings.LogType.ALL:
        should_log = True
    elif settings.log_types == settings.LogType.SUCCESS and success:
        should_log = True
    elif settings.log_types == settings.LogType.FAILED and not success:
        should_log = True

    if should_log:
        AccessReport.objects.create(
            ip_address=get_client_ip(request, settings),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            path_attempted=request.path,
            referer=request.META.get('HTTP_REFERER', ''),
            success=success,
            reason=reason,
        )
