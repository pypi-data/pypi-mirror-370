import datetime

import django_filters
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.auth import permission_denied
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.ui.tables import (
    BooleanColumn,
    Column,
    DateColumn,
)
from wagtail.admin.views.reports import ReportView
from wagtail.admin.widgets import AdminDateInput, BooleanRadioSelect
from wagtail.admin.widgets.button import (
    Button,
    ButtonWithDropdown,
    HeaderButton,
    ListingButton,
)

from .models import AccessReport


class AccessReportFilterSet(WagtailFilterSet):
    user_agent = django_filters.CharFilter(
        label=_('User Agent'),
        lookup_expr='icontains',
    )
    referer = django_filters.CharFilter(
        label=_('Referer'),
        lookup_expr='icontains',
    )
    path_attempted = django_filters.CharFilter(
        label=_('Path'),
        lookup_expr='icontains',
    )

    ip_address = django_filters.CharFilter(
        label=_('IP Address'),
        lookup_expr='icontains',
    )
    timestamp = django_filters.DateTimeFilter(
        label=_('Timestamp'),
        lookup_expr='lte',
        widget=AdminDateInput,
    )
    success = django_filters.BooleanFilter(
        label=_('Successful'),
        widget=BooleanRadioSelect,
    )

    class Meta:
        model = AccessReport
        fields = [
            'timestamp',
            'ip_address',
            'path_attempted',
            'success',
            'reason',
            'referer',
            'user_agent',
        ]


class AccessReportView(ReportView):
    model = AccessReport
    template_name = 'wagtailadmin/generic/index.html'
    header_icon = 'warning'
    page_title = 'Access Report'
    page_subtitle = 'Admin Login URL'
    paginate_by = 10
    name = 'access-report'
    menu_label = 'Admin Login URL'
    index_url_name = 'login_url_report'
    results_url_name = 'login_url_report_results'

    columns = [
        DateColumn('timestamp', label=_('Timestamp'), sort_key='timestamp'),
        Column('ip_address', label=_('IP Address'), sort_key='ip_address'),
        Column('path_attempted', label=_('Path'), sort_key='path_attempted'),
        BooleanColumn('success', label=_('Successful'), sort_key='success'),
        Column('reason', label=_('Reason'), sort_key='reason'),
        Column('referer', label=_('Referer'), sort_key='referer'),
        Column('user_agent', label=_('User Agent'), sort_key='user_agent', width='30%'),
    ]

    export_headings = {
        'pk': _('Report ID'),
        'timestamp': _('Timestamp'),
        'ip_address': _('IP Address'),
        'path_attempted': _('URL'),
        'success': _('Successful'),
        'referer': _('Referer'),
        'user_agent': _('User Agent'),
        'reason': _('Reasont'),
    }

    list_export = [
        'pk',
        'timestamp',
        'ip_address',
        'path_attempted',
        'success',
        'referer',
        'user_agent',
        'reason',
    ]

    search_fields = [
        'timestamp',
        'ip_address',
        'path_attempted',
        'success',
        'referer',
        'user_agent',
        'reason',
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clear_report(self, request, *args, **kwargs):
        AccessReport.objects.all().delete()

        from wagtail.admin import messages

        messages.success(request, _('Admin access logs have been cleared.'))

    def rotate_report(self, request, *args, **kwargs):
        from wagtail.admin import messages

        from .utils import cleanup_old_logs

        cleanup_old_logs()

        messages.success(request, _('Old access logs have been cleared.'))

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return permission_denied(request)

        if request.GET.get('clear_report') == '1':
            self.clear_report(request)

            # return redirect(self.index_url)
            return redirect(request.path)

        if request.GET.get('rotate_report') == '1':
            self.rotate_report(request)

            # return redirect(self.index_url)
            return redirect(request.path)

        return super().dispatch(request, *args, **kwargs)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.is_clear_report = request.GET.get('clear_report')

    def get_paginate_by(self, queryset):
        if self.is_clear_report:
            return None
        return super().get_paginate_by(queryset)

    def get_filename(self):
        return f'{self.name}-{datetime.datetime.today().strftime("%Y-%m-%d")}'

    @cached_property
    def filterset_class(self):
        if AccessReport.objects.count():
            return AccessReportFilterSet

    @cached_property
    def index_results_url(self):
        return reverse_lazy('login_url_report_results')
        # return 'hide_admin_report_results'

    def get_list_buttons(self, instance):
        more_buttons = []
        more_buttons.append(
            ListingButton(
                _('Edit'),
                url='https://google.com',
                icon_name='edit',
                attrs={'aria-label': _("Edit '%(title)s'") % {'title': str(instance)}},
                priority=10,
            )
        )

        buttons = []

        buttons.append(
            ButtonWithDropdown(
                buttons=more_buttons,
                icon_name='dots-horizontal',
                attrs={
                    'aria-label': _("More options for '%(title)s'") % {'title': str(instance)},
                },
            )
        )
        return buttons

    @property
    def rotate_report_url(self):
        params = self.request.GET.copy()
        params['rotate_report'] = '1'
        return self.request.path + '?' + params.urlencode()

    @property
    def clear_report_url(self):
        params = self.request.GET.copy()
        params['clear_report'] = '1'
        return self.request.path + '?' + params.urlencode()

    @cached_property
    def header_more_buttons(self) -> list:
        buttons = super().header_more_buttons.copy()
        if AccessReport.objects.count():
            buttons.append(
                Button(
                    _('Purge All Reports'),
                    url=self.clear_report_url,
                    # icon_name="rotate",
                    icon_name='bin',
                    priority=90,
                    attrs={'title': _('Delete all access logs')},
                )
            )

        return buttons

    @cached_property
    def header_buttons(self) -> list:
        buttons = super().header_buttons.copy()

        if AccessReport.objects.count():

            buttons.append(
                HeaderButton(
                    label=_('Purge Old Reports'),
                    # reverse("wagtailadmin_reports:workflow_tasks"),
                    url=self.rotate_report_url,
                    icon_name='rotate',
                    priority=90,
                    attrs={'title': _('Delete old access logs')},
                )
            )

        return buttons

    @cached_property
    def no_results_message(self):
        if self.is_searching or self.is_filtering:
            return _('No access records match your query.')

        return _('There are no access record to display.')

    @cached_property
    def is_searchable(self) -> bool:
        is_searchable = super().is_searchable

        if is_searchable and AccessReport.objects.count():
            return True

        return bool(is_searchable)
