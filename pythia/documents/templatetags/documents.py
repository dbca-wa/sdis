from django import template

from pythia.reports.models import ARARReport
from pythia.documents.models import Document

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_current_arar(context):
    """
    Get the latest ARAR report.
    """
    try:
        return ARARReport.objects.latest()
    except ARARReport.DoesNotExist:
        pass


@register.simple_tag
def document_status_label(document):
    labels = {
        Document.STATUS_NEW: 'danger',
        Document.STATUS_INREVIEW: 'warning',
        Document.STATUS_INAPPROVAL: 'info',
        Document.STATUS_APPROVED: 'success'
    }
    return '<span id="document_status" class="label label-%s">%s</span>' % (
        labels[document.status], document.get_status_display())

@register.simple_tag
def document_status_class(document):
    labels = {
        Document.STATUS_NEW: 'danger',
        Document.STATUS_INREVIEW: 'warning',
        Document.STATUS_INAPPROVAL: 'info',
        Document.STATUS_APPROVED: 'success'
    }
    return labels[document.status]


@register.inclusion_tag('admin/includes/document_details.html',
                        takes_context=True)
def document_details(context, document):
    """
    Render a document's details in a small sidebar.
    """
    return {
        'document': document,
        'request': context['request']
    }
