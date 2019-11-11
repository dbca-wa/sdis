"""This module contains models for Pythia Reports.

Currently, only the ARAR is implemented.
"""
from __future__ import (division, print_function, unicode_literals,
                        absolute_import)
import logging

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import signals
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django_resized import ResizedImageField

from pythia import models as pythia_models
from pythia.utils import texify_filename

from south.modelsinspector import add_introspection_rules
add_introspection_rules(
    [], ["^pythia\.reports\.models\.fields\.ResizedImageField"])

logger = logging.getLogger(__name__)


def reports_upload_to(instance, filename):
    """Create a custom upload location for user-submitted report images."""
    return "ararreports/{0}/{1}".format(
        instance.pk,
        texify_filename(filename)
    )


@python_2_unicode_compatible
class ARARReport(pythia_models.Audit):
    """
    The Annual Research Report.

    There can only be one ARR per year, enforced with a `unique` year.
    """

    year = models.PositiveIntegerField(
        verbose_name=_("Report year"),
        unique=True,
        validators=[MinValueValidator(2013)],
        help_text=_("The publication year of this report with four digits, "
                    "e.g. 2014 for the ARAR 2013-2014"))

    dm = models.TextField(
        verbose_name=_("Director's Message"),
        blank=True, null=True,
        help_text=_("The Director's Message in less than 10 000 words."))

    coverpage = models.FileField(
        upload_to=reports_upload_to, 
        blank=True, null=True,
        help_text="The cover page is provided from graphic designers"
                  " externally as on page A4 PDF.")

    rearcoverpage = models.FileField(
        upload_to=reports_upload_to, 
        blank=True, null=True,
        help_text="The back cover page is provided from graphic designers"
                  " externally as on page A4 PDF.")

    sds_chapterimage = ResizedImageField(
        upload_to=reports_upload_to,
        blank=True, null=True,
        size=[2480, 1240],
        help_text=_(
            "Upload a chapter image for the SDS chapter."
            " Aim for a visually quiet, low contrast image."
            " The horizon, if shown, should be in the top third and level."
            " The aspect ratio (width to height) must be 2:1."
            " The image will be resized to max 2480 (wt) x 1240 pt (ht)."
        )
    )

    sds_orgchart = ResizedImageField(
        upload_to=reports_upload_to,
        blank=True, null=True,
        size=[2480, 2480],
        help_text=_(
            "Upload an org chart for the SDS chapter."
            " The image will be resized to max 2480 (wt) x 2480 pt (ht)."
        )
    )

    sds_intro = models.TextField(
        verbose_name=_("Service Delivery Structure"),
        blank=True, null=True,
        help_text=_("Introduction paragraph for the Science Delivery Structure"
                    " section in the ARAR"))

    research_chapterimage = ResizedImageField(
        upload_to=reports_upload_to,
        blank=True, null=True,
        size=[2480, 1240],
        help_text=_(
            "Upload a chapter image for the Summary of Research projects."
            " Aim for a visually quiet, low contrast image."
            " The horizon, if shown, should be in the top third and level."
            " The aspect ratio (width to height) must be 2:1."
            " The image will be resized to max 2480 (wt) x 1240 pt (ht)."
        )
    )

    research_intro = models.TextField(
        verbose_name=_("Research Activities Introduction"),
        blank=True, null=True,
        help_text=_("Introduction paragraph for the Research Activity section "
                    "in the ARAR"))

    partnerships_chapterimage = ResizedImageField(
        upload_to=reports_upload_to,
        blank=True, null=True,
        size=[2480, 1240],
        help_text=_(
            "Upload a chapter image for the External Partnerships chapter."
            " Aim for a visually quiet, low contrast image."
            " The horizon, if shown, should be in the top third and level."
            " The aspect ratio (width to height) must be 2:1."
            " The image will be resized to max 2480 (wt) x 1240 pt (ht)."
        )
    )

    collaboration_chapterimage = ResizedImageField(
        upload_to=reports_upload_to,
        blank=True, null=True,
        size=[2480, 1240],
        help_text=_(
            "Upload a chapter image for the Collab with Academia summary."
            " Aim for a visually quiet, low contrast image."
            " The horizon, if shown, should be in the top third and level."
            " The aspect ratio (width to height) must be 2:1."
            " The image will be resized to max 2480 (wt) x 1240 pt (ht)."
        )
    )

    studentprojects_chapterimage = ResizedImageField(
        upload_to=reports_upload_to,
        blank=True, null=True,
        size=[2480, 1240],
        help_text=_(
            "Upload a chapter image for the Student Projects chapter."
            " Aim for a visually quiet, low contrast image."
            " The horizon, if shown, should be in the top third and level."
            " The aspect ratio (width to height) must be 2:1."
            " The image will be resized to max 2480 (wt) x 1240 pt (ht)."
        )
    )

    student_intro = models.TextField(
        verbose_name=_("Student Projects Introduction"),
        blank=True, null=True,
        help_text=_("Introduction paragraph for the Student Projects section "
                    "in the ARAR"))

    publications_chapterimage = ResizedImageField(
        upload_to=reports_upload_to,
        blank=True, null=True,
        size=[2480, 1240],
        help_text=_(
            "Upload a chapter image for the Publications chapter."
            " Aim for a visually quiet, low contrast image."
            " The horizon, if shown, should be in the top third and level."
            " The aspect ratio (width to height) must be 2:1."
            " The image will be resized to max 2480 (wt) x 1240 pt (ht)."
        )
    )

    pub = models.TextField(
        verbose_name=_("Publications and Reports"),
        blank=True, null=True,
        help_text=_("The Publications go here, Lisa!"))

    date_open = models.DateField(
        verbose_name=_("Open for submissions"),
        help_text=_("Date from which this ARAR report can be updated."))

    date_closed = models.DateField(
        verbose_name=_("Closed for submissions"),
        help_text=_("The cut-off date for any changes."))

    pdf = models.FileField(
        upload_to=reports_upload_to, 
        blank=True, null=True,
        editable=False,
        help_text="The latest, greatest and PDFest version of all times")    

    class Meta:
        """Class opts."""

        app_label = 'pythia'
        get_latest_by = 'date_open'  # 'created'
        verbose_name = 'Annual Research Report'
        verbose_name_plural = 'Annual Research Reports'

    def __str__(self):
        """The report name."""
        return "Annual Research Report {0}-{1}".format(
            self.year - 1, self.year)

    @property
    def fullname(self):
        """The HTML-safe report name."""
        return mark_safe(self.__str__())

    @property
    def download_title(self):
        """The PDF title."""
        return 'Annual Research Report'

    @property
    def download_subtitle(self):
        """The PDF subtitle."""
        return self.fullname

    @property
    def quicknav(self):
        """Some magic."""
        return None

    @property
    def progress_reports(self):
        """A QuerySet of Science Projects with prefetched documents."""
        return self.progressreport_set.all().order_by(
            "project__program",
            "project__position",
            "-project__year",
            "-project__number"
        ).prefetch_related(
            "project",
            "modifier",
            "project__program",
            "project__program__program_leader")

    @property
    def student_reports(self):
        """A QuerySet of StudentProjects with prefetched documents."""
        return self.studentreport_set.all().prefetch_related(
            "project",
            "modifier",
            "project__project_owner"
        ).order_by(
            "project__position",
            "project__project_owner__last_name",
            "-project__year",
            "-project__number")

    @property
    def collaboration_projects(self):
        """A QuerySet of CollaborationProjects with prefetched documents."""
        from pythia.projects.models import (Project, CollaborationProject as p)  # noqa
        return p.objects.filter(
            status=Project.STATUS_ACTIVE
        ).order_by("position", "-year", "-number")

    """
    @property
    def science_projects(self):
        from pythia.projects.models import (Project,
                ScienceProject as x,
                CoreFunctionProject as y)
        return Project.objects.filter(
                status__in=[Project.STATUS_ACTIVE,
                    Project.STATUS_CLOSING]
                #,Q(instance_of=x) | Q(instance_of=y)
            ).order_by(
                "program", "position", "-year", "-number"
            ).prefetch_related("documents")

    @property
    def programs(self):
        '''Returns a dict of programs / SPP and CF projects / ProgressReports
        '''
        from pythia.models import Program
        from pythia.projects.models import (Project,
                ScienceProject as SPP,
                CoreFunctionProject as CFP,
                CollaborationProject as COL,
                StudentProject as STP)
        from pythia.documents.models import (ProgressReport, StudentReport)
        PUBLISH = [Project.STATUS_ACTIVE, Project.STATUS_CLOSING]
        pr = ProgressReport.objects.filter(year=self.year)
        sr = StudentReport.objects.filter(year=self.year)
        spp = Project.objects.filter(
                status__in=PUBLISH
                #, Q(instance_of=SPP) | Q(instance_of=CFP)
                )

        # FIXME return a dict of PR and Project grouped by Program
        return Program.objects.filter(
            published__exact=True
            ).select_related('program_leader'
            ).prefetch_related(
                    'project_set',
                    'project_set__documents')
    """
    @property
    def opts(self):
        """The _meta class as property."""
        return self._meta


def call_update(proj, rep, final=False):
    """Request a (final) update from a project for a report.

    HACK: project status is set and saved, although the transition should do.
    """
    from pythia.projects.models import Project
    if final:
        proj.request_final_update(rep)
        proj.status = Project.STATUS_FINAL_UPDATE
    else:
        proj.request_update(rep)
        proj.status = Project.STATUS_UPDATE
    proj.save()
    logger.debug(
        "{0} processed request for progress report".format(proj.debugname))


def request_progress_reports(instance):
    """Call Project.request_update() for each active or closing project."""
    logger.debug("Function request_progress_reports() called.")
    from pythia.projects.models import (
        Project, ScienceProject, CoreFunctionProject, StudentProject)

    logger.debug("{0} requesting progress reports".format(instance.fullname))
    [call_update(Project.objects.get(pk=p), instance) for p in
        ScienceProject.objects.filter(status=Project.STATUS_ACTIVE
                                      ).values_list('pk', flat=True)]

    [call_update(Project.objects.get(pk=p), instance, final=True) for p in
        ScienceProject.objects.filter(status=Project.STATUS_CLOSING
                                      ).values_list('pk', flat=True)]

    [call_update(Project.objects.get(pk=p), instance) for p in
        CoreFunctionProject.objects.filter(status=Project.STATUS_ACTIVE
                                           ).values_list('pk', flat=True)]

    [call_update(Project.objects.get(pk=p), instance, final=True) for p in
        CoreFunctionProject.objects.filter(status=Project.STATUS_CLOSING
                                           ).values_list('pk', flat=True)]

    [call_update(Project.objects.get(pk=p), instance) for p in
        StudentProject.objects.filter(status=Project.STATUS_ACTIVE
                                      ).values_list('pk', flat=True)]
    logger.debug(
        "{0} finished requesting progressreports".format(instance.fullname))


def arar_post_save(sender, instance, created, **kwargs):
    """Post-save hook to request updates from relevant projects if necessary.

    A new ARAR requests updates from relevant projects.
    An existing ARAR will not request updates.
    """
    if created:
        logger.debug("ARARReport saved as new calls request_progress_reports.")
        request_progress_reports(instance)

signals.post_save.connect(arar_post_save, sender=ARARReport)
