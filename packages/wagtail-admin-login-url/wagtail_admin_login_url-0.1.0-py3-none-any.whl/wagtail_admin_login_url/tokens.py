import hashlib
import hmac

from django.conf import settings as django_settings
from django.http import HttpRequest

from wagtail_admin_login_url.models import Settings as AdminSettings


def generate_token(request: HttpRequest, settings: AdminSettings) -> str:
    secret = django_settings.SECRET_KEY.encode()
    fields = settings.verification_fields or []
    components = [request.META.get(field, '') for field in fields]
    message = '|'.join(components).encode()
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def has_valid_token(request: HttpRequest, settings: AdminSettings, session_key: str) -> bool:
    stored_token = request.session.get(session_key)
    if not stored_token:
        return False
    return stored_token == generate_token(request, settings)
