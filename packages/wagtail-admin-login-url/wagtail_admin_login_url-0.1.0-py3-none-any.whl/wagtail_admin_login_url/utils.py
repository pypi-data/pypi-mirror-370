import ipaddress
from datetime import timedelta

from django.http import HttpRequest
from django.utils.timezone import now

from wagtail_admin_login_url.models import AccessReport
from wagtail_admin_login_url.models import Settings as AdminSettings


def get_client_ip(request: HttpRequest, settings: AdminSettings | None = None) -> str:
    settings = settings or AdminSettings.load()
    for header in settings.get_trusted_headers():
        value = request.META.get(header)
        if value:
            ip = value.split(',')[0].strip()
            return ip
    return request.META.get('REMOTE_ADDR', '')


def is_ip_in_list(ip: str, entries: list[str]) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return False

    for entry in entries:
        try:
            if '/' in entry:
                if ip_obj in ipaddress.ip_network(entry, strict=False):
                    return True
            else:
                if ip_obj == ipaddress.ip_address(entry):
                    return True
        except ValueError:
            continue
    return False


def is_whitelisted(ip: str, settings: AdminSettings = AdminSettings.load()) -> bool:
    # settings = settings or AdminSettings.load()
    return is_ip_in_list(ip, settings.get_whitelist())


def is_blacklisted(ip: str, settings: AdminSettings = AdminSettings.load()) -> bool:
    # settings = settings or AdminSettings.load()
    return is_ip_in_list(ip, settings.get_blacklist())


def cleanup_old_logs():
    settings = AdminSettings.load()
    days = settings.log_retention_period
    threshold = now() - timedelta(days=days)
    AccessReport.objects.filter(timestamp__lt=threshold).delete()
