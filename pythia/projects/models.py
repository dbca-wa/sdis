"""
Classes for Projects within the Division.

Projects can be of different types, inheriting shared attributes and methods
from an abstract base class, while defining relevant project documentation
per class.

Projects are spatially defined through Areas of different types:
Administrative Regions (DPaW Regions and Districts, NRM/IBRA/IMCRA Regions),
Area of field work as the combined extent of sampling transects (if field work
occurs), Areas of relevance (Project findings apply to).
"""

from __future__ import (division, print_function, unicode_literals,
                        absolute_import)

from datetime import date
from itertools import chain
import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import signals
import django.db.models.options as options
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from django_fsm import FSMField, transition
from django_resized import ResizedImageField
from polymorphic import PolymorphicModel, PolymorphicManager

from pythia.documents.models import (
    ConceptPlan, ProgressReport, ProjectClosure, StudentReport)
from pythia.models import ActiveGeoModelManager, Audit, ActiveModel
from pythia.models import Program, WebResource, Division, Area, User
from pythia.reports.models import ARARReport
from pythia.utils import snitch, texify_filename

logger = logging.getLogger(__name__)

# Add additional attributes/methods to the model Meta class.
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('display_order',)


def projects_upload_to(instance, filename):
    """Create a custom upload location for user-submitted files."""
    return "projects/{0}-{1}/{2}".format(
        instance.year,
        instance.number,
        texify_filename(filename)
        )

NULL_CHOICES = (
    (None, _("Not applicable")),
    (False, _("Incomplete")),
    (True, _("Complete"))
    )


class ProjectManager(PolymorphicManager, ActiveGeoModelManager):
    """A custom Project Manager class."""

    pass


class PublishedProjectManager(PolymorphicManager, ActiveGeoModelManager):
    """A custom Project Manager class for publishable projects."""

    def get_queryset(self):
        """Default queryset: only publishable projects."""
        return super(PublishedProjectManager, self).get_queryset().filter(
            status__in=Project.PUBLISHED)


def get_next_available_number_for_year(year):
    """Return the lowest available project number for a given project year."""
    project_numbers = Project.objects.filter(year=year).values("number")
    if project_numbers.count() == 0:
        return 1
    else:
        return max([x['number'] for x in list(project_numbers)]) + 1


@python_2_unicode_compatible
class ResearchFunction(PolymorphicModel, Audit, ActiveModel):
    """A project contributes to a research function.

    Reports will summarise project progress reports bt research function.
    """

    name = models.TextField(
        verbose_name=_("Name"),
        help_text=_("The research function's name with formatting."))
    description = models.TextField(
        verbose_name=_("Description"),
        null=True, blank=True,
        help_text=_("The research function's description with formatting."))
    association = models.TextField(
        verbose_name=_("Association"),
        null=True, blank=True,
        help_text=_("The research function's association with "
                    "departmental programs."))
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("Function Leader"),
        related_name='pythia_researchfunction_leader',
        null=True, blank=True,
        help_text=_("The scientist in charge of the Research Function."))

    objects = ProjectManager()

    def __str__(self):
        """The name."""
        return mark_safe(strip_tags(self.name))


@python_2_unicode_compatible
class Project(PolymorphicModel, Audit, ActiveModel):
    """
    A Project is the core object in the system.

    A Project is an endeavour of a team of staff, where staff and financial
    resources are allocated to address a specific problen and achieve an
    outcome that reflects the priorities of divisional strategy.
    It should contain all the top (project) level attributes.

    A project has a start and end date, which is indicated by its own date
    fields.
    The life cycle stage of a project is indicated by its status field.
    The life cycle stage transitions are under control by its own can_<action>
    methods, which test whether a certain action is permitted considering
    the project's document approval statuses.
    """

    STATUS_NEW = 'new'
    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_UPDATE = 'updating'
    STATUS_CLOSURE_REQUESTED = 'closure requested'
    STATUS_CLOSING = 'closing'
    STATUS_FINAL_UPDATE = 'final update'
    STATUS_COMPLETED = 'completed'
    STATUS_TERMINATED = 'terminated'
    STATUS_SUSPENDED = 'suspended'

    ACTIVE = (STATUS_NEW, STATUS_PENDING, STATUS_ACTIVE, STATUS_UPDATE,
              STATUS_CLOSURE_REQUESTED, STATUS_CLOSING, STATUS_FINAL_UPDATE)
    PUBLISHED = (STATUS_ACTIVE, STATUS_UPDATE, STATUS_CLOSURE_REQUESTED,
                 STATUS_CLOSING, STATUS_FINAL_UPDATE, STATUS_COMPLETED)
    CLOSED = (STATUS_COMPLETED, STATUS_TERMINATED, STATUS_SUSPENDED)

    STATUS_CHOICES = (
        (STATUS_NEW, _("New project, pending concept plan approval")),
        (STATUS_PENDING, _("Pending project plan approval")),
        (STATUS_ACTIVE, _("Approved and active")),
        (STATUS_UPDATE, _("Update requested")),
        (STATUS_CLOSURE_REQUESTED,
            _("Closure pending approval of closure form")),
        (STATUS_CLOSING, _("Closure pending final update")),
        (STATUS_FINAL_UPDATE, _("Final update requested")),
        (STATUS_COMPLETED, _("Completed and closed")),
        (STATUS_TERMINATED, _("Terminated and closed")),
        (STATUS_SUSPENDED, _("Suspended")),
        )

    SCIENCE_PROJECT = 0
    CORE_PROJECT = 1
    COLLABORATION_PROJECT = 2
    STUDENT_PROJECT = 3
    PROJECT_TYPES = (
        (SCIENCE_PROJECT, _('Science Project')),
        (CORE_PROJECT, _('Core Function')),
        (COLLABORATION_PROJECT, _('External Collaboration')),
        (STUDENT_PROJECT, _('Student Project')),
        )

    PROJECT_ABBREVIATIONS = {
        SCIENCE_PROJECT: 'SP',
        CORE_PROJECT: 'CF',
        COLLABORATION_PROJECT: 'EXT',
        STUDENT_PROJECT: 'STP',
        }

    type = models.PositiveSmallIntegerField(
        verbose_name=_("Project type"),
        choices=PROJECT_TYPES,
        default=0,
        help_text=_("The project type determines the approval and "
                    "documentation requirements during the project's "
                    "life span. Choose wisely - you will not be able"
                    " to change the project type later."
                    "If you get it wrong, create a new project of the"
                    "correct type and tell admins to delete the duplicate "
                    "project of the incorrect type."))

    status = FSMField(
        default=STATUS_NEW,
        choices=STATUS_CHOICES,
        verbose_name=_("Project Status"))
    year = models.PositiveIntegerField(
        verbose_name=_("Project year"),
        # editable=False,
        default=lambda: date.today().year,
        help_text=_("The project year with four digits, e.g. 2014"))
    number = models.PositiveIntegerField(
        verbose_name=_("Project number"),
        default=lambda: get_next_available_number_for_year(date.today().year),
        help_text=_("The running project number within the project year."))
    position = models.IntegerField(
        blank=True, null=True, default=1000,
        help_text=_("The primary ordering instance. If left to default, "
                    "ordering happends by project year and number (newest "
                    "first)."))

    # -------------------------------------------------------------------------#
    # Name, image, slogan
    #
    title = models.TextField(
        verbose_name=_("Project title"),
        help_text=_("The project title with formatting if required."))
    image = ResizedImageField(
        upload_to=projects_upload_to,
        blank=True, null=True,
        help_text="Upload an image which represents the meaning, shows"
                  " a photogenic detail, or the team of the project."
                  " The image, if too large, will be resized to 600pt width."
                  " The original aspect ratio will be preserved."
                  " Aim for an aspect ratio (width to height) of 1.5 to 1.")
    tagline = models.TextField(
        blank=True, null=True,
        help_text="Sell the project in one sentence to a wide audience.")
    comments = models.TextField(
        blank=True, null=True,
        help_text=_("Any additional comments on the project."))
    keywords = models.TextField(
        blank=True, null=True,
        help_text="Add some keywords as comma separated list.")

    # -------------------------------------------------------------------------#
    # Time frame of project activity
    #
    start_date = models.DateField(
        null=True, blank=True,
        help_text=_("The project start date, update the initial estimate "
                    "later. Use format YYYY-MM-DD, e.g. 2014-12-31."))
    end_date = models.DateField(
        null=True, blank=True,
        help_text=_("The project end date, update the initial estimate "
                    "later. Use format YYYY-MM-DD, e.g. 2014-12-31."))

    # -------------------------------------------------------------------------#
    # Affiliation and linkages
    #
    program = models.ForeignKey(
        Program,
        verbose_name=_("Science and Conservation Division Program"),
        blank=True, null=True,
        help_text=_("The Science and Conservation Division Program hosting "
                    "this project."))
    output_program = models.ForeignKey(
        Division,
        verbose_name="Parks and Wildlife Service",
        blank=True, null=True,
        help_text=_("The DPaW service that this project delivers outputs to."))
    research_function = models.ForeignKey(
        ResearchFunction,
        blank=True, null=True,
        verbose_name="Research Function",
        help_text=_("The SCD Research Function this project mainly"
                    " contributes to."))
    areas = models.ManyToManyField(
        Area,
        blank=True,
        help_text="Areas of relevance")
    web_resources = models.ManyToManyField(
        WebResource,
        blank=True,
        help_text="Web resources of relevance: Data, Metadata, Wiki etc.")

    # -------------------------------------------------------------------------#
    # Important project roles
    #
    project_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("supervising scientist"),
        # clashes with sdis2
        related_name='pythia_project_owner',
        help_text=_("The supervising scientist."))
    data_custodian = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("data custodian"),
        # clashes with sdis2
        related_name='pythia_project_data_custodian', blank=True, null=True,
        help_text=_("The data custodian (SPP E25) responsible for data "
                    "management, publishing and metadata documentation"
                    " on the <a target=\"_\" href=\"http://internal-data.dpaw"
                    ".wa.gov.au/\">data catalogue</a>."))
    site_custodian = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("site custodian"),
        # clashes with sdis2
        related_name='pythia_project_site_custodian', blank=True, null=True,
        help_text=_("The site custodian responsible for georeferencing and "
                    "publishing study sites and putting them through "
                    "corporate approval to mitigate conflicts of study sites "
                    "and corporate activities."))
    members = models.ManyToManyField(
        User, through='projects.ProjectMembership')

    # -------------------------------------------------------------------------#
    # Dirty Hacks: lookups are read often, but change seldomly
    #
    team_list_plain = models.TextField(
        verbose_name="Team list",
        editable=False,
        null=True, blank=True,
        help_text=_("Team member names in order of membership rank."))
    supervising_scientist_list_plain = models.TextField(
        verbose_name="Supervising Scientists list",
        editable=False,
        null=True, blank=True,
        help_text=_("Supervising Scientist names in order of membership"
                    " rank. NOT the project owner, but all supervising "
                    "scientists on the team."))
    area_list_dpaw_region = models.TextField(
        verbose_name="DPaW Region List",
        editable=False, null=True, blank=True,
        help_text=_("DPaW Region names."))
    area_list_dpaw_district = models.TextField(
        verbose_name="DPaW Region List",
        editable=False, null=True, blank=True,
        help_text=_("DPaW Region names."))
    area_list_ibra_imcra_region = models.TextField(
        verbose_name="DPaW Region List",
        editable=False, null=True, blank=True,
        help_text=_("DPaW Region names."))
    area_list_nrm_region = models.TextField(
        verbose_name="DPaW Region List",
        editable=False, null=True, blank=True,
        help_text=_("DPaW Region names."))
    # end dirty hacks
    # -------------------------------------------------------------------------#

    objects = ProjectManager()
    published = PublishedProjectManager()

    class Meta:
        """Model options."""

        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        unique_together = (("year", "number"))
        ordering = ['position', '-year', '-number']
        get_latest_by = "start_date"
        permissions = (
            ('team', 'Contribute as team member'),
            )

    def __str__(self):
        """The project name: Type, year-number, title."""
        return "{0} {1}-{2:03d} {3}".format(
            Project.PROJECT_ABBREVIATIONS[self.type],
            self.year,
            self.number,
            strip_tags(self.title))

    @property
    def fullname(self):
        """The HTML-safe name."""
        return mark_safe(self.__str__())

    @property
    def debugname(self):
        """Return name and status for use in debug messages."""
        return "{0} ({1})".format(self.__str__(), self.status)

    def save(self, *args, **kwargs):
        """
        Save the project and call its setup method if created.

        The setup method is the transition into the state PROJECT_NEW.
        The project owner becomes a project member on project creation.
        The project number defaults to the next available number for the
        given project year.
        """
        created = True if not self.pk else False

        if not self.number:
            self.number = self.get_next_available_number()
        super(Project, self).save(*args, **kwargs)

        if created:
            self.setup()

    # Make self._meta accessible to templates
    @property
    def opts(self):
        """Return `._meta` as property."""
        return self._meta

    # -------------------------------------------------------------------------#
    # Project numbers
    @classmethod
    def get_next_available_number_for_year(cls, year):
        """Return the lowest available project number for a given year."""
        numbers = list(Project.objects.filter(year=year).values("number"))
        if len(numbers) == 0:
            return 1
        else:
            return max([x['number'] for x in Project.objects.filter(
                year=year).values("number")]) + 1

    def get_next_available_number(self):
        """Return the lowest available project number in the project's year."""
        return Project.get_next_available_number_for_year(self.year)

    """
    TODO: order field orders projects depending on type
    distribute to individual project classes?
    """
    # @property
    # def order_field(self):
    #    if self.project_type == 'COL':
    #        cd = self.get_doc('collaborationdetails')
    #        return cd.name
    #    if self.project_type == 'STP':
    #        return ('{0}, {1}'.format(self.project_owner.last_name,
    #        self.project_owner.first_name))
    #    else:
    #        return self.title

    # -------------------------------------------------------------------------#
    # audiences
    #
    @property
    def submitters(self):
        """Return all users with authority to author and "submit" this document.

        Default: project team members.
        """
        return list(set(self.members.filter(is_external=False)))

    @property
    def reviewers(self):
        """
        Return all users with authority to "review" this document.

        Default: The Program Leaders making up the SCMT.
        """
        # return [self.project.program.program_leader, ]
        # Alternative: all PLs = SMT
        # return Group.objects.get(name='SMT').user_set.all()
        try:
            smt, created = Group.objects.get_or_create(name='SMT')
            return smt.user_set.all()
        except:
            snitch("ERROR reviewers not found for {0}".format(self.debugname))
            return set()

    @property
    def reviewer(self):
        """Return the one reviewer to notify, the program leader."""
        return [self.program.program_leader, ]

    @property
    def approvers(self):
        """
        Return all users with permission to "approve" this document.

        Default: Divisional Directorate members.
        """
        try:
            scd, created = Group.objects.get_or_create(name='SCD')
            return scd.user_set.all()
        except:
            print("approvers not found")
            return set()
        # return Group.objects.get(name='SCD').user_set.all()

    @property
    def special_roles(self):
        """Return a deduplicated list of special roles.

        Special roles are:

        * Biometrician
        * Herbarium Curator
        * Animal Ethics representative
        * Data Manager

        """
        bm, created = Group.objects.get_or_create(name='BM')
        hc, created = Group.objects.get_or_create(name='HC')
        ae, created = Group.objects.get_or_create(name='AE')
        dm, created = Group.objects.get_or_create(name='DM')

        return list(set(chain(bm.user_set.all(),
                              hc.user_set.all(),
                              ae.user_set.all(),
                              dm.user_set.all())))

    @property
    def reviewer_approvers(self):
        """Return a deduplicated list of program leader and approvers."""
        return list(set(chain(self.reviewer, self.approvers)))

    @property
    def reviewers_approvers(self):
        """Return a deduplicated list of reviewers, approvers."""
        return list(set(chain(self.reviewers, self.approvers)))

    @property
    def all_involved(self):
        """List of submitters, program leader, approvers and special roles."""
        return list(set(chain(self.submitters, self.reviewer, self.approvers)))

    @property
    def all_permitted(self):
        """Return a deduplicated list of submitters, reviewers, approvers."""
        return list(
            set(chain(self.submitters, self.reviewers, self.approvers)))

    # -------------------------------------------------------------------------#
    # Project approval
    #
    def setup(self):
        """Perform post-save project setup."""
        pm, created = ProjectMembership.objects.get_or_create(
            project=self,
            user=self.project_owner,
            role=ProjectMembership.ROLE_SUPERVISING_SCIENTIST)

    # ACTIVE -> UPDATING -----------------------------------------------------#
    def can_request_update(self):
        """
        Gate-check prior to `request_update()`.

        Currently no checks. Does an ARAR need to exist?
        """
        return True

    @transition(
        field='status',
        source=STATUS_ACTIVE,
        target=STATUS_UPDATE,
        conditions=[can_request_update],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Request update",
            explanation="The project team can update and submit the "
            "annual progress report. Once the progress report is "
            "approved, the project will become 'active' again. If the "
            "project should have been closed, the Directorate can "
            "fast-track the project into the correct work flow.",
            notify=True,)
    )
    def request_update(self, report=None):
        """
        Transition to move the project to STATUS_UPDATING.

        Creates ProgressReport as required for SPP, CF.
        Override for STP to generate StudentReport, ignore for COL.
        """
        if report is None:
            report = ARARReport.objects.all().latest()
        self.make_progressreport(report)

    # ACTIVE -> CLOSURE_REQUESTED --------------------------------------------#
    def can_request_closure(self):
        """Gate-check prior to `request_closure()`. Currently no checks."""
        return True

    @transition(
        field='status',
        source=STATUS_ACTIVE,
        target=STATUS_CLOSURE_REQUESTED,
        conditions=[can_request_closure],
        permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(verbose="Request closure",
                    explanation="Once a project is completed as planned, "
                    "the normal closure process involves approval of the "
                    "ClosureForm, then a final ARAR progress report."
                    "Alternatively, immediate closure, suspension, or "
                    "termination can be requested as closure goal.",
                    notify=True,)
        )
    def request_closure(self):
        """Transition to move project to CLOSURE_REQUESTED.

        Creates ProjectClosure as required for SPP and CF,
        requires override to fast-track STP and COL to STATUS_COMPLETED.
        """
        pc, created = ProjectClosure.objects.get_or_create(project=self)

    # UPDATING -> CLOSURE_REQUESTED ------------------------------------------#
    def can_force_closure(self):
        """Gate check open."""
        return True

    @transition(
        field='status',
        source=STATUS_UPDATE,
        target=STATUS_CLOSURE_REQUESTED,
        conditions=[can_force_closure],
        permission=lambda instance, user: user in instance.reviewers_approvers,
        custom=dict(verbose="Force closure and cancel update",
                    explanation="If a project should have been closing, but "
                    "a progress report was requested in error, Program "
                    "Leaders and Directorate can cancel and delete the update "
                    "and fast-track the project into the closing state and "
                    "generate a ClosureForm. If the ClosureForm is approved "
                    "in time, the project can join the current ARAR for a "
                    "final update (requested by the Directorate), the "
                    "approval of which completes the project successfully.",
                    notify=True,)
        )
    def force_closure(self):
        """Transition to move project to CLOSURE_REQUESTED during UPDATING.

        Creates ProjectClosure as required for SPP and CF,
        requires override to fast-track STP and COL to STATUS_COMPLETED.

        Deletes current progressreport (warning - is it the right one?)
        Fast-tracks project to complete the update
        """
        pc, created = ProjectClosure.objects.get_or_create(project=self)
        self.progressreport.delete()

    # CLOSING -> FINAL_UPDATE ------------------------------------------------#
    def can_request_final_update(self):
        """
        Gate-check prior to `request_final_update()`.

        Return true if a final update can be requested before the project is
        closed. As long as project is in STATUS_CLOSING, the project is cleared
        to join in with the ARAR updates one last time.

        Therefore, currently no checks required.
        """
        return True

    @transition(
        field='status',
        source=STATUS_CLOSING,
        target=STATUS_FINAL_UPDATE,
        conditions=[can_request_final_update],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(verbose="Request final update",
                    explanation="A final progress report is required to "
                    "complete the project closure process. Team members can "
                    "update and submit the final update. Once the final "
                    "progress report is approved, the project is successfully"
                    " completed.",
                    notify=True,)
        )
    def request_final_update(self, report=None):
        """Transition to move the project to STATUS_FINAL_UPDATE."""
        if report is None:
            report = ARARReport.objects.latest()
        self.make_progressreport(report, final=True)

    # COMPLETED/TERM/SUSP -> ACTIVE ------------------------------------------#
    def can_reactivate(self):
        """
        Gate-check prior to `reactivate()`.

        Currently no checks.
        """
        return True

    @transition(
        field='status',
        source=CLOSED,
        target=STATUS_ACTIVE,
        conditions=[can_reactivate],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(verbose="Reactivate project",
                    explanation="The Directorate can reactivate a completed "
                    "project.",
                    notify=True,)
        )
    def reactivate(self):
        """Transition to move the project to its ACTIVE state."""
        return

    # EMAIL NOTIFICATIONS ----------------------------------------------------#
    def get_users_to_notify(self, target_status):
        """Return the appropriate audience to notify for a transition.

        TODO make specific to transition and include email template.
        """
        if target_status in [Project.STATUS_UPDATE,
                             Project.STATUS_FINAL_UPDATE,
                             Project.STATUS_CLOSING]:
            return self.submitters
        else:
            return set()

    # -------------------------------------------------------------------------#
    # Project labels and short codes
    #
    # Project code = "TYPE YEAR-NUMBER"
    @classmethod
    def clsm_project_year_number(cls, y, n):
        """Generate project year - number."""
        return '{0}-{1}'.format(y, str(n).zfill(3))

    @classmethod
    def clsm_project_type_year_number(cls, t, y, n):
        """Generate project type - year - number."""
        return '{0} {1}-{2}'.format(
            Project.PROJECT_ABBREVIATIONS[t], y, str(n).zfill(3))

    @classmethod
    def clsm_project_ckantag(cls, t, y, n):
        """Generate dash-separated project type - year - number."""
        return '{0}-{1}-{2}'.format(
            Project.PROJECT_ABBREVIATIONS[t], y, str(n).zfill(3))

    # Project name = "TYPE YEAR-NUMBER TITLE"
    @classmethod
    def clsm_project_type_year_number_name(cls, t, y, n, na):
        """Generate project type - year - padded number - name."""
        return mark_safe('{0} {1}-{2} {3}'.format(
            Project.PROJECT_ABBREVIATIONS[t], y, str(n).zfill(3), na))

    @property
    def project_type_year_number(self):
        """Return project type - year - padded number."""
        return Project.clsm_project_type_year_number(
            self.type, self.year, self.number)

    @property
    def project_type_year_number_plain(self):
        """Return project type - year - padded number as plain text."""
        return unicode(strip_tags(self.project_type_year_number)).strip()

    @property
    def project_ckantag(self):
        """Return dash-separated project type - year - number."""
        return Project.clsm_project_ckantag(
            self.type, self.year, self.number)

    @property
    def project_year_number(self):
        """Return project year - number."""
        return Project.clsm_project_year_number(self.year, self.number)

    @property
    def project_name_html(self):
        """Return the HTML-safe project type - year - number - title."""
        return Project.clsm_project_type_year_number_name(
            self.type, self.year, self.number, self.title)

    @property
    def project_title_html(self):
        """Return the HTML-safe project title."""
        return mark_safe(self.title)

    @property
    def title_plain(self):
        """Return a plain text version of the project title."""
        return unicode(strip_tags(self.title)).strip()

    @property
    def tagline_plain(self):
        """Return a plain text version of the project tagline."""
        return unicode(strip_tags(self.tagline)).strip()

    @property
    def comments_plain(self):
        """Return a plain text version of the project comments."""
        return unicode(strip_tags(self.comments)).strip()

    @property
    def keywords_plain(self):
        """Return a plain text version of the project keywords."""
        return unicode(strip_tags(self.keywords)) if self.keywords else ""

    @property
    def progressreport(self, year):
        """
        Stub to return the progress report for a given year.

        Instantiate in project classes as appropriate.
        """
        return None

    @property
    def status_display(self):
        """Return the human-readable status."""
        return self.get_status_display()

    @property
    def absolute_url(self):
        """Return the absolute url."""
        return self.get_absolute_url()
    # -------------------------------------------------------------------------#
    # Print
    #
    @property
    def download_title(self):
        """The PDF title."""
        return 'Project'

    @property
    def download_subtitle(self):
        """The PDF subtitle."""
        return self.fullname

    # -------------------------------------------------------------------------#
    # Team members
    #
    def get_team_list_plain(self):
        """Return a plain text version of the team list, DPAW staff only."""
        return ", ".join([
            m.user.abbreviated_name for m in
            self.projectmembership_set.select_related('user').filter(
                role__in=ProjectMembership.ROLES_STAFF).order_by(
                "position", "user__last_name", "user__first_name")])

    def get_supervising_scientist_list_plain(self):
        """Return a string of Supervising Scientist names."""
        return ', '.join([
            x.user.abbreviated_name for x in
            ProjectMembership.objects.filter(project=self).filter(
                role=ProjectMembership.ROLE_SUPERVISING_SCIENTIST)])

    @property
    def team_students(self):
        """Return a string of all team members in role Student."""
        return ', '.join([
            x.user.get_full_name() for x in
            ProjectMembership.objects.filter(
                project=self,
                role=ProjectMembership.ROLE_SUPERVISED_STUDENT)])

    @property
    def team_list(self):
        """
        Return a list of lists of project team memberships of staff roles only.

        The list contains:
        * the human-readable role,
        * the team member's full name,
        * the time allocation.
        """
        return[[m.get_role_display(), m.user.fullname, m.time_allocation] for m
               in self.projectmembership_set.select_related(
                    'user'
                ).filter(
                    role__in=ProjectMembership.ROLES_STAFF
                ).order_by(
                    "position", "user__last_name", "user__first_name")]

    # -------------------------------------------------------------------------#
    # Areas
    #
    @property
    def area_dpaw_district(self):
        """Return a string of all areas of type Dpaw District."""
        return ', '.join([area.name for area in self.areas.filter(
            area_type=Area.AREA_TYPE_DPAW_DISTRICT)])

    @property
    def area_dpaw_region(self):
        """Return a string of all areas of type Dpaw Region."""
        return ', '.join([area.name for area in self.areas.filter(
            area_type=Area.AREA_TYPE_DPAW_REGION)])

    @property
    def area_ibra_imcra_region(self):
        """Return a string of all areas of type IBRA or IMCRA Region."""
        return ', '.join([area.name for area in self.areas.filter(
            area_type__in=[Area.AREA_TYPE_IBRA_REGION,
                           Area.AREA_TYPE_IMCRA_REGION])])

    @property
    def area_nrm_region(self):
        """Return a string of all areas of type NRM Region."""
        return ', '.join([area.name for area in self.areas.filter(
            area_type=Area.AREA_TYPE_NRM_REGION)])


def project_areas_changed(sender, **kwargs):
    """
    Update cached Area names on Project.

    This method is called from a m2m_changed signal whenever
    project areas are changed.
    """
    p = kwargs['instance']
    p.area_list_dpaw_region = p.area_dpaw_region
    p.area_list_dpaw_district = p.area_dpaw_district
    p.area_list_ibra_imcra_region = p.area_ibra_imcra_region
    p.area_list_nrm_region = p.area_nrm_region
    p.save(update_fields=[
        'area_list_dpaw_region',
        'area_list_dpaw_district',
        'area_list_ibra_imcra_region',
        'area_list_nrm_region'])
signals.m2m_changed.connect(project_areas_changed,
                            sender=Project.areas.through)


class ScienceProject(Project):
    """
    An instantiated model for the main research project type.

    A Science Project is proposed by a Concept Plan, defined by a Project Plan,
    reported on annually by a Progress Report, and closed by a closure form
    after the last Progress Report.
    """

    class Meta:
        """Model options."""

        verbose_name = _("Science Project")
        verbose_name_plural = _("Science Projects")

    def setup(self):
        """Create a Conceptplan if not already existing. Make sure it's NEW."""
        pm, created = ProjectMembership.objects.get_or_create(
            project=self,
            user=self.project_owner,
            role=ProjectMembership.ROLE_SUPERVISING_SCIENTIST)
        scp, created = ConceptPlan.objects.get_or_create(project=self)
        from pythia.documents.models import Document
        scp.status = Document.STATUS_NEW
        scp.save(update_fields=['status', ])

    @property
    def progressreport(self):
        """Return the latest progress report or None.

        TODO returns the latest progress report, not using the year.
        """
        if not ProgressReport.objects.filter(project=self).exists():
            return None
        else:
            return self.documents.instance_of(ProgressReport).latest()

    def get_progressreport(self, year):
        """Return the ProgressReport for a given year."""
        if not ProgressReport.objects.filter(project=self, year=year).exists():
            a = ARARReport.objects.get(year=year)
            self.make_progressreport(a)
        return ProgressReport.objects.get(project=self, year=year)

    def make_progressreport(self, report, final=False):
        """Create (if neccessary) a ProgressReport for the given ARARReport.

        Populate fields from previous ProgressReport.
        Call this function for each participating project on ARAR creation.

        :param report: an instance of pythia.reports.models.ARARReport
        """
        msg = "Creating ProgressReport for {0}".format(self.__str__())
        snitch(msg)
        p, created = ProgressReport.objects.get_or_create(
            year=report.year, project=self)
        p.report = report
        p.is_final_report = final
        if (created and ProgressReport.objects.filter(
                project=self, year=report.year - 1).exists()):
            # This can go wrong:
            p0 = ProgressReport.objects.get(project=self, year=report.year - 1)
            p.context = p0.context
            p.aims = p0.aims
            p.progress = p0.progress
            p.implications = p0.implications
            p.future = p0.future
        p.save()
        msg = "{0} Added ProgressReport for year {1} in report {2}".format(
            p.project.project_type_year_number, p.year, p.report)
        snitch(msg)


class CoreFunctionProject(Project):
    """
    Instantiated class for departmental Core Function.

    A Core Function is without beginning.
    A Core Function is without end.
    There is no approval.
    There is no closure.
    Change comes from within.
    The Core Function answers only to the mighty ARARReport.
    """

    class Meta:
        """Model options."""

        verbose_name = _("Core Function")
        verbose_name_plural = _("Core Functions")

    def setup(self):
        """Setup a new CoreFunctionProject.

        Create a ProjectMembership for the project_owner,
        create a ConceptPlan.
        """
        pm, created = ProjectMembership.objects.get_or_create(
            project=self,
            user=self.project_owner,
            role=ProjectMembership.ROLE_SUPERVISING_SCIENTIST)
        scp, created = ConceptPlan.objects.get_or_create(project=self)
        from pythia.documents.models import Document
        scp.status = Document.STATUS_NEW
        scp.save(update_fields=['status', ])

    @property
    def progressreport(self):
        """Return the latest progress report or None. Same as ScienceProject.

        TODO returns the latest progress report, not using the year.
        """
        if not ProgressReport.objects.filter(project=self).exists():
            return None
        else:
            return self.documents.instance_of(ProgressReport).latest()

    def get_progressreport(self, year):
        """Return the ProgressReport for a given year."""
        if not ProgressReport.objects.filter(project=self, year=year).exists():
            a = ARARReport.objects.get(year=year)
            self.make_progressreport(a)
        return ProgressReport.objects.get(project=self, year=year)

    def make_progressreport(self, report, final=False):
        """Create (if neccessary) a ProgressReport for the given ARARReport.

        Populate fields from previous ProgressReport.
        Call this function for each participating project on ARAR creation.

        :param report: an instance of pythia.reports.models.ARARReport
        """
        msg = "Creating ProgressReport for {0}".format(self.__str__())
        logger.info(msg)
        if settings.DEBUG:
            print(msg)
        p, created = ProgressReport.objects.get_or_create(
                year=report.year, project=self)
        p.report = report
        p.is_final_report = final
        if (created and ProgressReport.objects.filter(
                project=self, year=report.year - 1).exists()):
            # This can go wrong:
            p0 = ProgressReport.objects.get(project=self, year=report.year - 1)
            p.context = p0.context
            p.aims = p0.aims
            p.progress = p0.progress
            p.implications = p0.implications
            p.future = p0.future
        p.save()
        msg = "{0} Added ProgressReport for year {1} in report {2}".format(
            p.project.project_type_year_number, p.year, p.report)
        logger.info(msg)
        if settings.DEBUG:
            print(msg)


class CollaborationProject(Project):
    """
    Instantiated class for external Collaboration.

    An external Collaboration with academia, industry or government
    requires only registration, but no Progress Reports.
    """

    name = models.TextField(
        max_length=2000,
        verbose_name=_("Collaboration name (with formatting)"),
        help_text=_("The collaboration name with formatting if required."))
    budget = models.TextField(
        verbose_name=_("Total Budget"),
        help_text=_("Specify the total financial and staff time budget."))

    staff_list_plain = models.TextField(
            verbose_name="DPaW Involvement",
            editable=False,
            null=True, blank=True,
            help_text=_("Staff names in order of membership rank."
                        " Update by adding DPaW staff as team members."))

    class Meta:
        """Model options."""

        verbose_name = _("External Partnership")
        verbose_name_plural = _("External Partnerships")

    @transition(
        field='status',
        source=Project.STATUS_NEW,
        target=Project.STATUS_ACTIVE,
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(verbose="Setup Project", notify=False,)
        )
    def setup(self):
        """A collaboration project is automatically approved and active."""
        self.status = Project.STATUS_ACTIVE
        self.save(update_fields=['status', ])

    def get_staff_list_plain(self):
        """Return a string of DPaW staff."""
        return ', '.join([
            x.user.abbreviated_name for x in
            ProjectMembership.objects.filter(project=self).filter(
                role__in=[
                    ProjectMembership.ROLE_SUPERVISING_SCIENTIST,
                    ProjectMembership.ROLE_RESEARCH_SCIENTIST,
                    ProjectMembership.ROLE_TECHNICAL_OFFICER
                    ])
            ])

    # Forbid actions non applicable to this project type
    def can_request_update(self):
        """
        Gate-check prior to `request_update()`.

        Currently no checks. Does an ARAR need to exist?
        """
        return False

    @transition(
        field='status',
        source=Project.STATUS_ACTIVE,
        target=Project.STATUS_UPDATE,
        conditions=[can_request_update],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(verbose="Request update",
                    explanation="The project team can update and submit the "
                    "annual progress report. Once the progress report is "
                    "approved, the project will become 'active' again. If the "
                    "project should have been closed, the Directorate can "
                    "fast-track the project into the correct work flow.",
                    notify=True,)
        )
    def request_update(self, report=None):
        """
        Transition to move the project to STATUS_UPDATING.

        Creates ProgressReport as required for SPP, CF.
        Override for STP to generate StudentReport, ignore for COL.
        """

    def can_request_closure(self):
        """Gate-check prior to `request_closure()`. Currently no checks."""
        return False

    @transition(
        field='status',
        source=Project.STATUS_ACTIVE,
        target=Project.STATUS_CLOSURE_REQUESTED,
        conditions=[can_request_closure],
        permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(verbose="Request closure",
                    explanation="Once a project is completed as planned, "
                    "the normal closure process involves approval of the "
                    "ClosureForm, then a final ARAR progress report."
                    "Alternatively, immediate closure, suspension, or "
                    "termination can be requested as closure goal.",
                    notify=True,)
        )
    def request_closure(self):
        """Transition to move project to CLOSURE_REQUESTED.

        Creates ProjectClosure as required for SPP and CF,
        requires override to fast-track STP and COL to STATUS_COMPLETED.
        """

    def can_force_closure(self):
        """Prevent force closure for CollaborationProjects."""
        return False

    @transition(
        field='status',
        source=Project.STATUS_ACTIVE,
        target=Project.STATUS_COMPLETED,
        permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(verbose="Close project", explanation="", notify=False,)
        )
    def complete(self):
        """External CollaborationProjects complete without closure process."""
        return

    @transition(
        field='status',
        source=Project.STATUS_COMPLETED,
        target=Project.STATUS_ACTIVE,
        permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(verbose="Reactivate project",
                    explanation="The project team can reactivate a completed "
                    "project.",
                    notify=True,)
        )
    def reactivate(self):
        """Transition to move the project to its ACTIVE state."""
        return


class StudentProject(Project):
    """
    Instantiated class for StudentProjects.

    Student Projects are academic collaborations involving a student's
    work, can be started without divisional approval and only require
    annual Progress Reports.
    """

    LEVEL_PHD = 0
    LEVEL_MSC = 1
    LEVEL_HON = 2
    LEVEL_4TH = 3
    LEVEL_3RD = 4
    LEVEL_UND = 5
    LEVEL_PDC = 6

    LEVELS = (
        (LEVEL_PDC, "Post-Doc"),
        (LEVEL_PHD, "PhD"),
        (LEVEL_MSC, "MSc"),
        (LEVEL_HON, "BSc (Honours)"),
        (LEVEL_4TH, "Yr 4 intern"),
        (LEVEL_3RD, "3rd year"),
        (LEVEL_UND, "Undergraduate project"),
        )

    level = models.PositiveSmallIntegerField(
        null=True, blank=True, choices=LEVELS, default=LEVEL_PHD,
        help_text=_("The academic qualification achieved through this "
                    "project."))
    organisation = models.TextField(
        verbose_name=_("Academic Organisation"), blank=True, null=True,
        help_text=_("The full name of the academic organisation."))

    student_list_plain = models.TextField(
            verbose_name="Student list",
            editable=False,
            null=True, blank=True,
            help_text=_("Student names in order of membership rank."))
    academic_list_plain = models.TextField(
            verbose_name="Academic",
            editable=False,
            null=True, blank=True,
            help_text=_("Academic supervisors in order of membership rank."
                        " Update by adding team members as academic "
                        "supervisors."))
    academic_list_plain_no_affiliation = models.TextField(
            verbose_name="Academic without affiliation",
            editable=False,
            null=True, blank=True,
            help_text=_("Academic supervisors without their affiliation "
                        "in order of membership rank. Update by adding team "
                        "members as academic supervisors."))

    class Meta:
        """Model options."""

        verbose_name = _("Student Project")
        verbose_name_plural = _("Student Projects")

    @property
    def sort_value(self):
        """Return a value to sort all objects of this class by."""
        return self.project_owner.last_name

    def get_student_list_plain(self):
        """Return a string of Student names."""
        return ', '.join([
            x.user.abbreviated_name for x in
            ProjectMembership.objects.filter(project=self).filter(
                role=ProjectMembership.ROLE_SUPERVISED_STUDENT)])

    def get_academic_list_plain(self):
        """Return a string of DPaW staff."""
        return ', '.join([
            x.user.abbreviated_name for x in
            ProjectMembership.objects.filter(project=self).filter(
                role=ProjectMembership.ROLE_ACADEMIC_SUPERVISOR)])

    def get_academic_list_plain_no_affiliation(self):
        """Return a string of DPaW staff without their affiliation."""
        return ', '.join([
            x.user.abbreviated_name_no_affiliation for x in
            ProjectMembership.objects.filter(project=self).filter(
                role=ProjectMembership.ROLE_ACADEMIC_SUPERVISOR)])

    @property
    def academic(self):
        """Return a string of the Academic Supervisor name(s)."""
        return ', '.join([
            x.user.abbreviated_name for x in
            ProjectMembership.objects.filter(project=self).filter(
                role=ProjectMembership.ROLE_ACADEMIC_SUPERVISOR)])

    @property
    def academic_no_affiliation(self):
        """Academic Supervisor name(s) without their affiliations."""
        return ', '.join([
            x.user.abbreviated_name_no_affiliation for x in
            ProjectMembership.objects.filter(project=self).filter(
                role=ProjectMembership.ROLE_ACADEMIC_SUPERVISOR)])

    @property
    def organisation_plain(self):
        """The academic organisation as plain text."""
        return mark_safe(strip_tags(self.organisation))

    def setup(self):
        """A student project becomes active without approval process."""
        self.status = Project.STATUS_ACTIVE
        self.save(update_fields=['status', ])

    @transition(
        field='status',
        source=Project.STATUS_ACTIVE,
        target=Project.STATUS_UPDATE,
        # conditions=[can_request_update]
        permission="approve",
        custom=dict(verbose="Request update", explanation="", notify=True,)
        )
    def request_update(self, report=None):
        """The Student Report replaces the Progress Report."""
        if report is None:
            report = ARARReport.objects.all().latest()
        self.make_progressreport(report)
        return None

    def can_request_final_update(self):
        """Prevent final updates for StudentProjects."""
        return False

    def can_request_closure(self):
        """Gate-check prior to `request_closure()`. Currently no checks."""
        return False

    @transition(
        field='status',
        source=Project.STATUS_ACTIVE,
        target=Project.STATUS_CLOSURE_REQUESTED,
        conditions=[can_request_closure],
        permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(verbose="Request closure",
                    explanation="Once a project is completed as planned, "
                    "the normal closure process involves approval of the "
                    "ClosureForm, then a final ARAR progress report."
                    "Alternatively, immediate closure, suspension, or "
                    "termination can be requested as closure goal.",
                    notify=True,)
        )
    def request_closure(self):
        """Transition to move project to CLOSURE_REQUESTED.

        Creates ProjectClosure as required for SPP and CF,
        requires override to fast-track STP and COL to STATUS_COMPLETED.
        """
        return

    @transition(
        field='status',
        source=Project.STATUS_UPDATE,
        target=Project.STATUS_COMPLETED,
        permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(verbose="Force closure and cancel update",
                    explanation="If a StudentProject should have been closed"
                    ", but an ARAR has erroneously requested an update, "
                    "the project team or their line management can close "
                    "the project without any further process. Doing so will"
                    "remove the unwanted progress report.",
                    notify=True,)
        )
    def force_closure(self):
        """Transition to move project to COMPLETED during UPDATING.

        All involved staff can run this tx on a StudentProject for which
        an ARAR update was requested, but which should have been closed.

        The permission to run this tx is given to all involved, as closure
        can be requested for a StudentProject by all involved staff, and does
        not require a formal process.

        Deletes current progressreport (warning - is it the right one?)
        """
        self.progressreport.delete()

    @transition(
        field='status',
        source=Project.STATUS_ACTIVE,
        target=Project.STATUS_COMPLETED,
        permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(verbose="Close project",
                    explanation="The project team or their line management "
                    "can request the closure of an active StudentProject, "
                    "which immediately completes without any further process.",
                    notify=False,)
        )
    def complete(self):
        """Allow StudentProjects to complete without closure process."""
        return

    @transition(
        field='status',
        source=Project.STATUS_COMPLETED,
        target=Project.STATUS_ACTIVE,
        # conditions=[Project.can_reactivate],
        permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(verbose="Reactivate project",
                    explanation="The project team can reactivate a completed "
                    "project.",
                    notify=True,)
        )
    def reactivate(self):
        """Transition to move the project to its ACTIVE state."""
        return

    @property
    def progressreport(self):
        """Return the latest progress report.

        TODO returns the latest progress report, not using the year.
        """
        if self.documents.instance_of(StudentReport).exists():
            return self.documents.instance_of(StudentReport).latest()
        else:
            return None

    def get_progressreport(self, year):
        """Return the StudentReport for a given year."""
        if not StudentReport.objects.filter(project=self, year=year).exists():
            a = ARARReport.objects.get(year=year)
            self.make_progressreport(year, a.id)
        return ProgressReport.objects.get(project=self, year=year)

    def make_progressreport(self, report):
        """Create (if neccessary) a StudentReport for the given year.

        Populate fields from previous StudentReport.
        Call this for each participating project when creating an ARAR.

        :param year: the integer year of the StudentReport delivery,
            e.g. 2014 for FY2013-14
        :param report: an instance of ARARReport
        """
        logger.info("Creating ProgressReport for {0}".format(self.__str__()))
        p, created = StudentReport.objects.get_or_create(
                year=report.year, project=self)
        p.report = report
        if (created and StudentReport.objects.filter(
                project=self, year=report.year - 1).exists()):
            p0 = StudentReport.objects.get(project=self, year=report.year - 1)
            p.progress_report = p0.progress_report
        p.save()
        msg = "{0} Added StudentReport for year {1} in report {2}".format(
            p.project.project_type_year_number, p.year, p.report)
        snitch(msg)


PROJECT_CLASS_MAP = {
    Project.SCIENCE_PROJECT: ScienceProject,
    Project.CORE_PROJECT: CoreFunctionProject,
    Project.COLLABORATION_PROJECT: CollaborationProject,
    Project.STUDENT_PROJECT: StudentProject
    }


@python_2_unicode_compatible
class ProjectMembership(models.Model):
    """Project memberships link projects and people."""

    ROLE_SUPERVISING_SCIENTIST = 1
    ROLE_RESEARCH_SCIENTIST = 2
    ROLE_TECHNICAL_OFFICER = 3
    ROLE_EXTERNAL_PEER = 4
    ROLE_CONSULTED_PEER = 5
    ROLE_ACADEMIC_SUPERVISOR = 6
    ROLE_SUPERVISED_STUDENT = 7
    ROLE_EXTERNAL_COLLABORATOR = 8
    ROLE_GROUP = 9

    ROLE_CHOICES = (
        (ROLE_SUPERVISING_SCIENTIST, "Supervising Scientist"),
        (ROLE_RESEARCH_SCIENTIST, "Research Scientist"),
        (ROLE_TECHNICAL_OFFICER, "Technical Officer"),
        (ROLE_EXTERNAL_COLLABORATOR, "External Collaborator"),
        (ROLE_ACADEMIC_SUPERVISOR, "Academic Supervisor"),
        (ROLE_SUPERVISED_STUDENT, "Supervised Student"),
        (ROLE_EXTERNAL_PEER, "External Peer"),
        (ROLE_CONSULTED_PEER, "Consulted Peer"),
        (ROLE_GROUP, "Involved Group")
        )

    ROLES_STAFF = (
        ROLE_SUPERVISING_SCIENTIST,
        ROLE_RESEARCH_SCIENTIST,
        ROLE_TECHNICAL_OFFICER
        )

    project = models.ForeignKey(
        Project, help_text=_("The project for the team membership."))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_("The DPaW staff member to participate in the project "
                    "team."))
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES,
        help_text=_("The role this team member fills within this project."))
    time_allocation = models.FloatField(
        blank=True, null=True, default=0,
        verbose_name=_("Time allocation (0 to 1 FTE)"),
        help_text=_("Indicative time allocation as a fraction of a Full Time "
                    "Equivalent (220 person-days). Values between 0 and 1."))
    position = models.IntegerField(
        blank=True, null=True, verbose_name=_("List position"), default=100,
        help_text=_("The lowest position number comes first in the team "
                    "members list. Ignore to keep alphabetical order, "
                    "increase to shift member towards the end of the list, "
                    "decrease to promote member to beginning of the list."))
    comments = models.TextField(
        blank=True, null=True,
        help_text=_("Any comments clarifying the project membership."))

    class Meta:
        """Model options."""

        ordering = ['position']
        verbose_name = _("Project Membership")
        verbose_name_plural = _("Project Memberships")

    def __str__(self):
        """A HTML-safe description of the ProjectMembership."""
        msg = "{0} ({1} - {2} - {3} FTE) [List position {4}] {5}"
        return mark_safe(msg.format(
            self.user.__str__(),
            self.project.project_type_year_number,
            self.get_role_display(), self.time_allocation,
            self.position, self.comments))


def refresh_project_cache(p):
    """Refresh all cached area and team fields of a Project p."""
    p.area_list_dpaw_region = p.area_dpaw_region
    p.area_list_dpaw_district = p.area_dpaw_district
    p.area_list_ibra_imcra_region = p.area_ibra_imcra_region
    p.area_list_nrm_region = p.area_nrm_region
    p.team_list_plain = p.get_team_list_plain()
    p.supervising_scientist_list_plain = \
        p.get_supervising_scientist_list_plain()
    p.save(update_fields=[
            'area_list_dpaw_region',
            'area_list_dpaw_district',
            'area_list_ibra_imcra_region',
            'area_list_nrm_region',
            'team_list_plain',
            'supervising_scientist_list_plain'])
    if (p._meta.model_name == 'studentproject'):
        p.student_list_plain = p.get_student_list_plain()
        p.academic_list_plain = p.get_academic_list_plain()
        p.academic_list_plain_no_affiliation = \
            p.get_academic_list_plain_no_affiliation()
        p.save(update_fields=['student_list_plain', 'academic_list_plain', ])
        # p.staff_list_plain = p.get_staff_list_plain()
        # p.save(update_fields=['staff_list_plain'])
    return True


def refresh_all_project_caches():
    """Refresh cached project membership and area lists."""
    tmp = [refresh_project_cache(p) for p in
           Project.objects.select_related("projectmembership_set", "area_set")]
    return len(tmp)


def refresh_project_member_cache_fields(projectmembership_instance,
                                        remove=False):
    """Refresh the cached Project.team_list_plain, student and staff lists."""
    try:
        p = projectmembership_instance.project
    except Project.DoesNotExist:
        return
    p.team_list_plain = p.get_team_list_plain()
    p.save(update_fields=['team_list_plain'])

    # give user permission to change team?
    # if remove:
    #    print("remove user permission to change/delete team memberships")
    # TODO remove user's permissions on documents
    # else:
    #    print("grant user permission to change/delete team memberships")

    # some crazyness for StudentProjects and CollaborationProjects
    if (projectmembership_instance.role ==
            ProjectMembership.ROLE_SUPERVISING_SCIENTIST):
        p.supervising_scientist_list_plain = \
            p.get_supervising_scientist_list_plain()
        p.save(update_fields=['supervising_scientist_list_plain'])
    if (projectmembership_instance.role ==
            ProjectMembership.ROLE_SUPERVISED_STUDENT and
            p._meta.model_name == 'studentproject'):
        p.student_list_plain = p.get_student_list_plain()
        p.save(update_fields=['student_list_plain'])
    if (projectmembership_instance.role ==
            ProjectMembership.ROLE_ACADEMIC_SUPERVISOR and
            p._meta.model_name == 'studentproject'):
        p.academic_list_plain = p.get_academic_list_plain()
        p.academic_list_plain_no_affiliation = \
            p.get_academic_list_plain_no_affiliation()
        p.save(update_fields=['academic_list_plain',
                              'academic_list_plain_no_affiliation', ])
    if (p._meta.model_name == 'collaborationproject'):
        p.staff_list_plain = p.get_staff_list_plain()
        p.save(update_fields=['staff_list_plain'])


def projectmembership_post_save(sender, instance, created, **kwargs):
    """
    Refresh cached project membership lists and document permissions.

    SYNCDB Comment out post-syncdb and post-save hooks before
     running loaddata to dev/test/uat or restoring database
    """
    refresh_project_member_cache_fields(instance)
    # from pythia.documents.utils import update_document_permissions as udp
    # [udp(d) for d in instance.project.documents.all()]
signals.post_save.connect(projectmembership_post_save,
                          sender=ProjectMembership)


def projectmembership_post_delete(sender, instance, using, **kwargs):
    """Post delete hook to refresh cached project membership lists.

    Built-in fail safe against project being deleted: only runs if instance
    exists.
    """
    refresh_project_member_cache_fields(instance, remove=True)
signals.post_delete.connect(projectmembership_post_delete,
                            sender=ProjectMembership)


def project_pre_delete(sender, instance, using, **kwargs):
    """Project pre delete: Delete related documents and team memberships.

    This avoids confusion and heartache for document and membership hooks.
    """
    [d.delete() for d in instance.documents.all()]
    [m.delete() for m in instance.projectmembership_set.all()]
signals.pre_delete.connect(project_pre_delete, sender=Project)
