from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.admin.widgets import SwitchInput
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting


@register_setting(icon='cog')
class Settings(BaseGenericSetting):
    class VerificationField(models.TextChoices):
        REMOTE_ADDR = 'REMOTE_ADDR', 'Remote Address (IP) - ✅ Strong base token'
        HTTP_USER_AGENT = 'HTTP_USER_AGENT', 'User Agent - ✅ Adds entropy'
        HTTP_ACCEPT_LANGUAGE = 'HTTP_ACCEPT_LANGUAGE', 'Accept-Language - ✅ Optional'
        HTTP_REFERER = 'HTTP_REFERER', 'Referrer - Use carefully - ⚠️ Use carefully'
        HTTP_ACCEPT_ENCODING = 'HTTP_ACCEPT_ENCODING', 'Accept-Encoding - ✅ Adds variety'
        HTTP_ACCEPT = 'HTTP_ACCEPT', 'Accept - ⚠️ admin sprite and jsi18n issues'
        HTTP_CONNECTION = 'HTTP_CONNECTION', 'Connection - ⚠️ Often changes randomly'

    class LogType(models.TextChoices):
        FAILED = 'failed', _('Failed Access')
        SUCCESS = 'success', _('Successful Access')
        ALL = 'all', _('Failed and Successful')

    _admin_path = models.CharField(
        blank=False,
        default='portal/',
        max_length=100,
        verbose_name=_('Admin Path'),
        # help_text=_('Custom path for accessing the Wagtail admin (e.g., "dashboard").'),
        help_text=_('The secret path to access admin if hide-admin is enabled. Example: "dashboard".'),
    )

    session_timeout = models.PositiveIntegerField(
        default=300,
        validators=[MinValueValidator(60), MaxValueValidator(3600)],
        verbose_name=_('Session Timeout (seconds)'),
        help_text=_(
            'Time the temporary admin session remains valid for non-authenticated users (e.g., 300 = 5 minutes).'
        ),
        # help_text=_("Session lifetime for temporary admin access token."),
    )

    verification_fields = MultiSelectField(
        choices=VerificationField.choices,
        default=[VerificationField.REMOTE_ADDR, VerificationField.HTTP_USER_AGENT],
        verbose_name=_('Verification Fields'),
        # help_text=_("Select which request attributes to use when generating access tokens."),
        help_text=_('Headers used to sign and verify the admin token.'),
    )

    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enable Hide Admin Protection'),
        # help_text=_("When enabled, unauthenticated users must access Wagtail admin via the custom path."),
        help_text=_('If enabled, unauthenticated users must use the secret path to access the Wagtail admin.'),
    )

    # Admin Logging Configuration

    logging_enabled = models.BooleanField(
        verbose_name=_('Enable Logging'),
        default=True,
        help_text=_('Enable or disable admin access logging.'),
    )
    log_types = models.CharField(
        verbose_name=_('Log Types'),
        max_length=255,
        choices=LogType.choices,
        default=LogType.FAILED,
        help_text=_('Types of logs to record.'),
    )
    # TODO: Implement Periodic Cleanup of Old Logs
    # See: cron.py or management/commands/cleanup_logs.py
    log_retention_period = models.PositiveIntegerField(
        verbose_name=_('Log Retention Period (Days)'),
        default=30,
        help_text=_('Delete logs older than this many days.'),
    )

    # Login throttling
    throttling_login_enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enable Login Throttling'),
        help_text=_('Enable or disable login throttling per IP.'),
    )

    throttle_attempt_limit = models.PositiveIntegerField(
        default=4,
        verbose_name=_('Max Attempts Before Lockout'),
        help_text=_('Number of failed attempts before initial lockout.'),
    )

    throttle_lockout_duration = models.PositiveIntegerField(
        default=20,
        verbose_name=_('Initial Lockout Duration (minutes)'),
        help_text=_('Lockout duration in minutes after reaching the attempt limit.'),
    )

    throttle_escalation_threshold = models.PositiveIntegerField(
        default=2,
        verbose_name=_('Escalation Threshold'),
        help_text=_('How many lockouts in 24 hours before escalating to longer lockout.'),
    )

    throttle_escalated_duration = models.PositiveIntegerField(
        default=1440,
        verbose_name=_('Escalated Lockout Duration (minutes)'),
        help_text=_('Lockout duration (in minutes) when escalated. 1440 = 24 hours.'),
    )

    throttle_window = models.PositiveIntegerField(
        default=1440,
        verbose_name=_('Throttle Window (minutes)'),
        help_text=_('Time window to track failed attempts and lockout history (default 1440 = 24h).'),
    )

    ip_whitelist = models.TextField(
        blank=True,
        verbose_name=_('IP Whitelist'),
        help_text=_('One IP or IP range per line. These IPs will never be throttled. Ex. 127.0.0.1'),
    )
    ip_blacklist = models.TextField(
        blank=True,
        verbose_name=_('IP Blacklist'),
        help_text=_('One IP or IP range per line. These IPs will always be blocked. Ex. 127.0.0.1/24'),
    )

    trusted_ip_headers = models.TextField(
        # blank=True,
        default='REMOTE_ADDR',
        verbose_name=_('Trusted IP Origins'),
        help_text=_('One header per line (e.g., REMOTE_ADDR, HTTP_X_FORWARDED_FOR). Default is REMOTE_ADDR.'),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('enabled', widget=SwitchInput()),
                FieldRowPanel([
                    FieldPanel(
                        '_admin_path',
                        # help_text=_('Custom path for accessing the Wagtail admin (e.g., "dash").'),
                    ),
                    FieldPanel('session_timeout'),
                ]),
            ],
            # heading=_('Admin Logging Configuration'),
        ),
        FieldPanel('verification_fields'),
        MultiFieldPanel(
            [
                FieldPanel('ip_whitelist'),
                FieldPanel('ip_blacklist'),
                FieldPanel(
                    'trusted_ip_headers',
                    help_text=(
                        'Specify the origins you trust in order of priority, separated by commas. '
                        'We strongly recommend that you do not use anything other than REMOTE_ADDR '
                        'since other origins can be easily faked. '
                        'Examples: REMOTE_ADDR, HTTP_X_FORWARDED_FOR, HTTP_CF_CONNECTING_IP, HTTP_X_SUCURI_CLIENTIP '
                    ),
                ),
            ],
            heading=_('IP Settings'),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('throttling_login_enabled', widget=SwitchInput()),
                    FieldPanel('throttle_attempt_limit'),
                    FieldPanel('throttle_lockout_duration'),
                ]),
                FieldRowPanel([
                    FieldPanel('throttle_escalation_threshold'),
                    FieldPanel('throttle_escalated_duration'),
                    FieldPanel('throttle_window'),
                ]),
            ],
            heading=_('Login Throttling'),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel([
                    FieldPanel('logging_enabled', widget=SwitchInput()),
                    FieldPanel('log_types'),
                    FieldPanel('log_retention_period'),
                ]),
            ],
            heading=_('Logging Configuration'),
        ),
    ]

    @property
    def admin_path(self):
        return self._admin_path.strip().strip('/')

    def get_trusted_headers(self):
        if ',' in self.trusted_ip_headers:
            lines = self.trusted_ip_headers.strip().split(',')
        else:
            lines = self.trusted_ip_headers.strip().splitlines()
        return [line.strip() for line in lines if line.strip()] or ['REMOTE_ADDR']

    def get_whitelist(self):
        if ',' in self.ip_whitelist:
            return [line.strip() for line in self.ip_whitelist.strip().split(',') if line.strip()]
        return [line.strip() for line in self.ip_whitelist.strip().splitlines() if line.strip()]

    def get_blacklist(self):
        if ',' in self.ip_blacklist:
            return [line.strip() for line in self.ip_blacklist.strip().split(',') if line.strip()]
        return [line.strip() for line in self.ip_blacklist.strip().splitlines() if line.strip()]

    class Meta:
        verbose_name = _('Admin Login URL')
        verbose_name_plural = _('Admin Login URL')


class AccessReport(models.Model):
    class Reason(models.TextChoices):
        WHITELISTED = 'Whitelisted', _('Whitelisted')
        BLACKLISTED = 'Blacklisted', _('Blacklisted')
        TOKEN_VALID = 'Token Valid', _('Valid Token')
        SECRET_PATH_ACCESSED = 'Secret Path Accessed', _('Secret Path Accessed')
        RESTRICTED_PATH_ATTEMPT = 'Restricted Path Attempt', _('Restricted Path Attempt')
        INVALID_PATH_ATTEMPT = 'Invalid Path Attempt', _('Invalid Path Attempt')
        SESSION_TIMEOUT_EXPIRED = 'Session Timeout Expired', _('Session Timeout Expired')
        TOO_MANY_ATTEMPTS_LOCKED_OUT = 'Too Many Attempts - Locked Out', _('Too Many Attempts - Locked Out')
        FAILED_LOGIN_THROTTLED = 'FailedLoginThrottled', _('Failed Login - Throttled')
        THROTTLING_DISABLED = 'Throttling Disabled', _('Throttling Disabled')
        HIDE_ADMIN_DISABLED = 'Hide Admin Disabled', _('Hide Admin Disabled')
        AUTHENTICATED_USER = 'Authenticated User', _('Authenticated User')
        INVALID_SECRET_PATH = 'Invalid Secret Path', _('Invalid Secret Path')
        MISSING_SESSION_TOKEN = 'Missing Session Token', _('Missing Session Token')
        LOCKOUT_ESCALATED = 'Lockout Escalated', _('Lockout Escalated')
        LOCKOUT_INITIAL = 'Lockout Initial', _('Initial Lockout')
        UNKNOWN = 'Unknown', _('Unknown or Unexpected Condition')

    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True, editable=False)
    user_agent = models.TextField(blank=True, editable=False)
    path_attempted = models.CharField(max_length=255)
    referer = models.CharField(max_length=255, blank=True)
    success = models.BooleanField(default=False)
    reason = models.CharField(
        max_length=64,
        choices=Reason.choices,
        default=Reason.UNKNOWN,
        verbose_name=_("Reason"),
        help_text=_("Reason the access attempt was logged."),
    )

    class Meta:
        verbose_name = 'Access Report'
        verbose_name_plural = 'Access Reports'
        ordering = ['-timestamp']

    def __str__(self) -> str:
        return f'{self.timestamp} {self.path_attempted}'
