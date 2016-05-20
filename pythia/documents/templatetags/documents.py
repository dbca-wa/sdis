"""pythia.documents Templatetags."""
from django import template

from pythia.reports.models import ARARReport
from pythia.documents.models import Document

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_current_arar(context):
    """Get the latest ARAR report."""
    try:
        return ARARReport.objects.latest()
    except ARARReport.DoesNotExist:
        pass


@register.simple_tag
def document_status_label(document):
    """Return an HTML span for a document status."""
    labels = {
        Document.STATUS_NEW: 'danger',
        Document.STATUS_INREVIEW: 'warning',
        Document.STATUS_INAPPROVAL: 'info',
        Document.STATUS_APPROVED: 'success'
        }
    return ('<span id="doc_status_{0}" class="label label-{1}">{2}'
            '</span>'.format(
                document.pk,
                labels[document.status],
                document.get_status_display()))


@register.simple_tag
def document_status_class(document):
    """Return the twitter-bootstrap CSS class name for a given doc status."""
    labels = {
        Document.STATUS_NEW: 'danger',
        Document.STATUS_INREVIEW: 'warning',
        Document.STATUS_INAPPROVAL: 'info',
        Document.STATUS_APPROVED: 'success'
        }
    return labels[document.status]


@register.inclusion_tag(
    'admin/includes/document_details.html', takes_context=True)
def document_details(context, document):
    """Render a document's details in a small sidebar."""
    return {'document': document, 'request': context['request']}
