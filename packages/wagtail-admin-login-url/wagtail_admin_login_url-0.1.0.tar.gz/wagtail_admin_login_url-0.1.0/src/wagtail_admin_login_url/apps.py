from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailAdminLoginURLAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wagtail_admin_login_url"
    label = 'wagtail_admin_login_url'
    verbose_name = _("Admin Login URL")
    verbose_name_plural = _("Admin Login URL")

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
