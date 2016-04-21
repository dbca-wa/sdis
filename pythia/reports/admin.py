from __future__ import unicode_literals, absolute_import

from pythia.admin import BaseAdmin, DownloadAdminMixin, DetailAdmin


class ARARReportAdmin(BaseAdmin, DownloadAdminMixin, DetailAdmin):
    download_template = "arar"

    def queryset(self, request):
        return super(ARARReportAdmin, self).queryset(request)
