from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import AdminOnlyMenuItem

from .views import AccessReportView


@hooks.register('register_reports_menu_item')
def register_hide_admin_report_menu_item():
    return AdminOnlyMenuItem(
        AccessReportView.menu_label,
        reverse(AccessReportView.index_url_name),
        icon_name=AccessReportView.header_icon,
        order=700,
    )


@hooks.register('register_admin_urls')
def register_hide_admin_report_url():
    return [
        path(
            'reports/login-url/',
            AccessReportView.as_view(),
            name=AccessReportView.index_url_name,
        ),
        path(
            'reports/login-url/results/',
            AccessReportView.as_view(results_only=True),
            name=AccessReportView.results_url_name,
        ),
    ]

