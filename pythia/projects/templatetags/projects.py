"""pythia.documents Templatetags."""
from django import template

from pythia.projects.models import Project

register = template.Library()

@register.simple_tag
def project_status_label(project):
    """Return an HTML span for a project status."""
    labels = {
        Project.STATUS_NEW: 'danger',
        Project.STATUS_PENDING: 'warning',
        Project.STATUS_ACTIVE: 'success',
        Project.STATUS_UPDATE: 'primary',
        Project.STATUS_CLOSURE_REQUESTED: 'info',
        Project.STATUS_CLOSING: 'info',
        Project.STATUS_FINAL_UPDATE: 'primary',
        Project.STATUS_COMPLETED: 'success',
        Project.STATUS_TERMINATED: 'success',
        Project.STATUS_SUSPENDED: 'success',
        }
    return ('<span id="pro_status_{0}" class="label label-{1}">{2}'
            '</span>'.format(
                project.pk,
                labels[project.status],
                project.get_status_display()))
