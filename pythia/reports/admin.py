from __future__ import unicode_literals, absolute_import

from pythia.admin import BaseAdmin, DownloadAdminMixin, DetailAdmin


class ARARReportAdmin(BaseAdmin, DownloadAdminMixin, DetailAdmin):
    download_template = "arar"
    list_display = ('__str__', 'year', 'date_open', 'date_closed')

    def queryset(self, request):
        return super(ARARReportAdmin, self).queryset(request)
