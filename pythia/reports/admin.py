from __future__ import unicode_literals, absolute_import

from swingers.admin import DetailAdmin

from pythia.admin import BaseAdmin, DownloadAdminMixin

class ARARReportAdmin(BaseAdmin, DownloadAdminMixin, DetailAdmin):
    download_template = "arar"
    def queryset(self, request):
        return super(ARARReportAdmin, self).queryset(request)
