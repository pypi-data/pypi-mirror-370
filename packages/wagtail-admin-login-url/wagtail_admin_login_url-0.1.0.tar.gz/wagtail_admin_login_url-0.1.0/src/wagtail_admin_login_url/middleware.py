# from django.conf import settings as django_settings
from django.http import Http404, HttpRequest, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

from wagtail_admin_login_url.models import AccessReport
from wagtail_admin_login_url.models import Settings as HideAdminSettings
from wagtail_admin_login_url.reports import log_access
from wagtail_admin_login_url.throttling import LimitLoginAttempts
from wagtail_admin_login_url.tokens import generate_token, has_valid_token
from wagtail_admin_login_url.utils import get_client_ip, is_blacklisted, is_whitelisted


class AdminLoginURLMiddleware:
    SESSION_KEY = '_wagtail_admin_login_url_access'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.user.is_authenticated:
            # log_access(request=request, success=True, reason=AccessReport.Reason.AUTHENTICATED_USER)
            return self.get_response(request)

        settings = HideAdminSettings.load()

        if not settings.enabled:
            self._clear_token(request)

            # log_access(request=request, success=True, reason=AccessReport.Reason.HIDE_ADMIN_DISABLED)
            return self.get_response(request)

        ip = get_client_ip(request, settings)

        if is_blacklisted(ip, settings):
            log_access(request=request, success=False, reason=AccessReport.Reason.BLACKLISTED)
            raise Http404('IP blacklisted')

        if is_whitelisted(ip, settings):
            log_access(request=request, success=True, reason=AccessReport.Reason.WHITELISTED)
            return self.get_response(request)

        # limiter = LimitLoginAttempts(request)
        # throttler = LimitLoginAttempts(ip, settings)

        # if throttler.is_enabled() and throttler.is_locked_out():
        #     return HttpResponseForbidden("Too many failed login attempts. Try again later.")
        throttler = LimitLoginAttempts(request)

        if throttler.is_locked_out():
            log_access(request=request, success=False, reason=AccessReport.Reason.TOO_MANY_ATTEMPTS_LOCKED_OUT)
            return HttpResponseForbidden(AccessReport.Reason.TOO_MANY_ATTEMPTS_LOCKED_OUT)

        request_path = request.path.strip('/')
        admin_path = settings.admin_path
        actual_admin_path = reverse('wagtailadmin_home').strip('/')
        actual_login_path = reverse('wagtailadmin_login').strip('/')

        if has_valid_token(request, settings, self.SESSION_KEY):
            if request_path == admin_path:
                # log_access(request=request, success=True, reason=AccessReport.Reason.TOKEN_VALID)
                return redirect(f'/{actual_login_path}/')

            # log_access(request=request, success=True, reason=AccessReport.Reason.TOKEN_VALID)
            return self.get_response(request)

        if request_path == admin_path:
            token = generate_token(request, settings)
            request.session[self.SESSION_KEY] = token
            request.session.set_expiry(settings.session_timeout)
            log_access(request=request, success=True, reason=AccessReport.Reason.SECRET_PATH_ACCESSED)
            return redirect(f'/{actual_login_path}/')

        if request_path == actual_admin_path or request_path.startswith(f'{actual_admin_path}/'):
            throttler.register_failed_attempt()
            log_access(request=request, success=False, reason=AccessReport.Reason.RESTRICTED_PATH_ATTEMPT)
            raise Http404('Not Found')

        return self.get_response(request)

    def _clear_token(self, request: HttpRequest):
        if self.SESSION_KEY in request.session:
            del request.session[self.SESSION_KEY]
