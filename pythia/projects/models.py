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
# import json
import logging
# import markdown

from django.conf import settings
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.auth.models import Permission
# from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import signals
import django.db.models.options as options
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from django_fsm.db.fields import FSMField, transition
from polymorphic import PolymorphicModel, PolymorphicManager

from pythia.documents.models import (
    ConceptPlan, ProjectPlan, ProgressReport, ProjectClosure, StudentReport)
from pythia.models import ActiveGeoModelManager, Audit, ActiveModel
from pythia.models import Program, WebResource, Division, Area, User
from pythia.reports.models import ARARReport

logger = logging.getLogger(__name__)

# Add additional attributes/methods to the model Meta class.
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('display_order',)


def projects_upload_to(instance, filename):
    """Create a custom upload location for user-submitted files."""
    return "projects/{0}-{1}/{2}".format(
        instance.year, instance.number, filename)

NULL_CHOICES = ((None, _("Not applicable")), (False, _("Incomplete")),
                (True, _("Complete")))


class ProjectManager(PolymorphicManager, ActiveGeoModelManager):
    """A custom Project Manager class."""

    pass


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
        (STATUS_SUSPENDED, _("Suspended"))
    )

    SCIENCE_PROJECT = 0
    CORE_PROJECT = 1
    COLLABORATION_PROJECT = 2
    STUDENT_PROJECT = 3
    PROJECT_TYPES = (
        (SCIENCE_PROJECT, _('Science project')),
        (CORE_PROJECT, _('Core function project')),
        (COLLABORATION_PROJECT, _('Collaboration project')),
        (STUDENT_PROJECT, _('Student project')),
    )

    PROJECT_ABBREVIATIONS = {
        SCIENCE_PROJECT: 'SP',
        CORE_PROJECT: 'CF',
        COLLABORATION_PROJECT: 'EXT',
        STUDENT_PROJECT: 'STP'
    }

    type = models.PositiveSmallIntegerField(
        verbose_name=_("Project type"),
        choices=PROJECT_TYPES,
        default=0,
        help_text=_("The project type determines the approval and "
                    "documentation requirements during the project's "
                    "life span. Choose wisely - you will not be able"
                    " to change the project type later."))

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
    image = models.ImageField(
        upload_to=projects_upload_to,
        blank=True, null=True,
        help_text="Upload an image which represents the meaning, or shows"
                  " a nice detail, or the team of the project.")
    tagline = models.TextField(
        blank=True, null=True,
        help_text="Sell the project in one sentence to a wide audience.")
    comments = models.TextField(
        blank=True, null=True,
        help_text=_("Any additional comments on the project."))

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

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        unique_together = (("year", "number"))
        ordering = ['position', '-year', '-number']

    def __str__(self):
        """The project name: Type, year-number, title."""
        return mark_safe("%s %s-%s %s" % (
            self.get_type_display(),
            self.year, self.number,
            strip_tags(self.title)))

    @property
    def fullname(self):
        """The HTML-safe name."""
        return mark_safe(self.__str__())

    def save(self, *args, **kwargs):
        """
        Save the project and call its setup method.

        The setup method is the transition into the state PROJECT_NEW.

        The project owner is a project member by default (refs SDIS-241):
        If created, add a ProjectMembership for the project owner.
        """
        created = True if not self.pk else False

        if not self.number:
            self.number = self.get_next_available_number()
        super(Project, self).save(*args, **kwargs)

        if created:
            ProjectMembership.objects.create(
                project=self,
                user=self.project_owner,
                role=ProjectMembership.ROLE_SUPERVISING_SCIENTIST)
            self.setup()

    # Make self._meta accessible to templates
    @property
    def opts(self):
        """Return `._meta` as property."""
        return self._meta

    # -------------------------------------------------------------------------#
    # Project numbers
    @classmethod
    def get_next_available_number_for_year(year):
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

    """TODO: order field orders projects depending on type
    distribute to individual project classes?"""
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
    # Project approval
    #
    def setup(self):
        """Perform post-save project setup."""
        pass

    # NEW -> PENDING ---------------------------------------------------------#
    def can_endorse(self):
        """
        Gate-check prior to `endorse()`.

        A science project or core function can only become PENDING if its
        Concept Plan has been approved.
        Other projects are fast-tracked to status PROJECT_ACTIVE on `setup()`.
        """
        try:
            has_approved_conceptplan = self.documents.instance_of(
                    ConceptPlan).latest().is_approved
            msg = "Approved ConceptPlan found: {0}".format(
                    has_approved_conceptplan)
            logger.info(msg)
            if settings.DEBUG:
                print(msg)
            return has_approved_conceptplan
        except:
            msg = "ConceptPlan not found but required for project.endorse()!"
            logger.info(msg)
            if settings.DEBUG:
                print(msg)
            return False

    @transition(field=status,
                save=True,
                verbose_name=_("Endorse Project"),
                source=STATUS_NEW,
                target=STATUS_PENDING,
                conditions=['can_endorse'],
                permission="approve",
                )
    def endorse(self):
        """
        Transition to move project to PENDING.

        Generates ProjectPlan as required for SPP and CF, skipped by others.
        """
        msg = "Project.endorse() about to add a ProjectPlan"
        logger.info(msg)
        if not self.documents.instance_of(ProjectPlan):
            ProjectPlan.objects.create(
                    project=self,
                    creator=self.creator,
                    modifier=self.modifier)
        msg = self.__dict__
        logger.info(msg)
        if settings.DEBUG:
            print(msg)

    # PENDING -> ACTIVE ------------------------------------------------------#
    def can_approve(self):
        """
        Gate-check prior to `approve()`.

        A project can only become ACTIVE if its Project Plan is approved.
        """
        try:
            return self.documents.instance_of(ProjectPlan).latest().is_approved
        except:
            logger.info('ProjectPlan not found! Cannot approve Project without'
                        ' approved ProjectPlan!')
            return False

    @transition(field=status,
                save=True,
                verbose_name=_("Approve Project"),
                source=STATUS_PENDING,
                target=STATUS_ACTIVE,
                conditions=['can_approve'],
                permission="approve")
    def approve(self):
        """Transition to move the project to ACTIVE."""
        return

    # ACTIVE -> UPDATING -----------------------------------------------------#
    def can_request_update(self):
        """
        Gate-check prior to `request_update()`.

        Currently no checks. Does an ARAR need to exist?
        """
        return True

    @transition(field=status,
                save=True,
                verbose_name=_("Request update"),
                source=STATUS_ACTIVE,
                target=STATUS_UPDATE,
                conditions=['can_request_update'],
                permission="approve")
    def request_update(self, report=None):
        """
        Transition to move the project to STATUS_UPDATING.

        Creates ProgressReport as required for SPP, CF.
        Override for STP to generate StudentReport, ignore for COL.
        """
        if report is None:
            report = ARARReport.objects.all().latest()
        self.make_progressreport(report)
        return

    # UPDATING --> ACTIVE ----------------------------------------------------#
    def can_complete_update(self):
        """
        Gate-check prior to `complete_update()`.

        Allow the update to be complete when the document has been approved.
        WARNING: will check against the latest progress report to be approved.
        Could return True if no current ProgressReport has been requested and
        previous ProgressReport is approved. Assumes that `request_update()`
        has been called, and new projects joining the party during an active
        ARAR reporting cycle will get their `request_update()` called.

        Needs override for STP to check for StudentReport to be approved.
        """
        try:
            return self.documents.instance_of(
                ProgressReport).latest().is_approved
        except:
            logger.info('ProgressReport not found! Cannot complete update '
                        'without approved Progress Report!')
            return False

    @transition(field=status,
                save=True,
                verbose_name=_("Complete update"),
                source=STATUS_UPDATE,
                target=STATUS_ACTIVE,
                # conditions=['can_complete_update'],
                permission="submit")
    def complete_update(self):
        """
        Move the project back to ACTIVE after finishing its update.

        WARNING Currently skips the gate check!
        """
        return

    # ACTIVE -> CLOSURE_REQUESTED --------------------------------------------#
    def can_request_closure(self):
        """
        Gate-check prior to `request_closure()`.

        Currently no checks.
        """
        return True

    @transition(field=status,
                save=True,
                verbose_name=_("Request closure"),
                source=STATUS_ACTIVE,
                target=STATUS_CLOSURE_REQUESTED,
                conditions=['can_request_closure'],
                permission="submit",
                )
    def request_closure(self):
        """Transition to move project to CLOSURE_REQUESTED.

        Creates ProjectClosure as required for SPP and CF,
        requires override to fast-track STP and COL to STATUS_COMPLETED.
        """
        ProjectClosure.objects.create(
            project=self,
            creator=self.creator,
            modifier=self.modifier)

    @transition(field=status,
                save=True,
                verbose_name=_("Force closure and cancel update"),
                source=STATUS_UPDATE,
                target=STATUS_CLOSURE_REQUESTED,
                conditions=['can_request_closure'],
                permission="review")
    def force_closure(self):
        """Transition to move project to CLOSURE_REQUESTED during UPDATING.

        Creates ProjectClosure as required for SPP and CF,
        requires override to fast-track STP and COL to STATUS_COMPLETED.

        Deletes current progressreport (warning - is it the right one?)
        Fast-tracks project to complete the update
        """
        ProjectClosure.objects.create(
            project=self,
            creator=self.creator,
            modifier=self.modifier)
        # TODO: delete Progressreports of currently active ARAR
        self.progressreport.delete()

    # CLOSURE_REQUESTED -> CLOSING -------------------------------------------#
    def can_accept_closure(self):
        """
        Gate-check prior to `accept_closure()`.

        Allow the update to progress to closing if the closure form
        has been approved.

        TODO: insert gate checks: is the projectplan updated with latest data
        management info, is the closure form approved
        """
        return self.documents.instance_of(ProjectClosure).latest().is_approved

    @transition(field=status,
                save=True,
                verbose_name=_("Accept closure"),
                source=STATUS_CLOSURE_REQUESTED,
                target=STATUS_CLOSING,
                conditions=['can_accept_closure'],
                permission="approve")
    def accept_closure(self):
        """Transition to move the project to CLOSING."""
        return

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

    @transition(field=status,
                verbose_name=_("Request final update"),
                save=True,
                source=[STATUS_CLOSING, STATUS_COMPLETED],
                target=STATUS_FINAL_UPDATE,
                conditions=['can_request_final_update'],
                permission="approve")
    def request_final_update(self):
        """Transition to move the project to STATUS_FINAL_UPDATE."""
        ProgressReport.objects.create(
            project=self,
            creator=self.creator,
            modifier=self.modifier,
            is_final_report=True,
            year=date.today().year)

    # FINAL_UPDATE -> COMPLETED ----------------------------------------------#
    def can_complete(self):
        """
        Gate-check prior to `complete()`.

        Projects can be completed if the final progress report and project
        closure are approved.
        """
        lpr = self.documents.instance_of(ProgressReport).latest()
        return (lpr.is_final_report and
                lpr.is_approved and
                self.documents.instance_of(
                    ProjectClosure).latest().is_approved)

    @transition(field=status,
                verbose_name=_("Complete final update"),
                save=True,
                source=STATUS_FINAL_UPDATE,
                target=STATUS_COMPLETED,
                # conditions=['can_complete'],
                permission="approve")
    def complete(self):
        """
        Transition to move the project to its COMPLETED state.

        No more actions are required of this project.
        Only reactivate() should be possible now.
        """
        return

    # ACTIVE -> COMPLETED ----------------------------------------------------#
    @transition(field=status,
                verbose_name=_("Force-complete project"),
                save=True,
                source=STATUS_ACTIVE,
                target=STATUS_COMPLETED,
                # conditions=['can_complete'],
                permission="review")
    def force_complete(self):
        """
        Force-choke the project to its COMPLETED state.

        Available to Reviewers on active projects.
        Project Members must go through the official process.
        No more actions are required of this project.
        Only reactivate() should be possible now.
        """
        # if self.status == Project.STATUS_UPDATE:
        #    self.progressreport.delete()

    # COMPLETED -> ACTIVE ----------------------------------------------------#
    def can_reactivate(self):
        """
        Gate-check prior to `reactivate()`.

        Currently no checks.
        """
        return True

    @transition(field=status,
                verbose_name=_("Reactivate project"),
                save=True,
                source=STATUS_COMPLETED,
                target=STATUS_ACTIVE,
                conditions=['can_reactivate'],
                permission="approve")
    def reactivate(self):
        """Transition to move the project to its ACTIVE state."""
        return

    # ACTIVE -> TERMINATED ---------------------------------------------------#
    def can_terminate(self):
        """Return true if the project can be reactivated."""
        return True

    @transition(field=status,
                verbose_name=_("Terminate project"),
                save=True,
                source=STATUS_ACTIVE,
                target=STATUS_TERMINATED,
                conditions=['can_terminate'],
                permission="approve")
    def terminate(self):
        """Transition the project to its TERMINATED state."""
        return

    # TERMINATED -> ACTIVE ---------------------------------------------------#
    def can_reactivate_terminated(self):
        """Whether the project can be reactivated from being terminated."""
        return True

    @transition(field=status,
                verbose_name=_("Reactivate terminated project"),
                save=True,
                source=STATUS_TERMINATED,
                target=STATUS_ACTIVE,
                conditions=['can_reactivate_terminated'],
                permission="approve")
    def reactivate_terminated(self):
        """Transition the project to its ACTIVE state."""
        return

    # ACTIVE -> SUSPENDED ----------------------------------------------------#
    def can_suspend(self):
        """Return true if the project can be suspended."""
        return True

    @transition(field=status,
                verbose_name=_("Suspend project"),
                save=True,
                source=STATUS_ACTIVE,
                target=STATUS_SUSPENDED,
                conditions=['can_suspend'],
                permission="approve")
    def suspend(self):
        """Transition the project to its SUSPENDED state."""
        return

    # SUSPENDED -> ACTIVE ----------------------------------------------------#
    def can_reactivate_suspended(self):
        """Whether the project can be reactivated from suspension."""
        return True

    @transition(field=status,
                save=True,
                verbose_name=_("Reactivate suspended project"),
                source=STATUS_SUSPENDED,
                target=STATUS_ACTIVE,
                conditions=['can_reactivate_suspended'],
                permission="approve")
    def reactivate_suspended(self):
        """Transition the suspended project to its ACTIVE state."""
        return

    # EMAIL NOTIFICATIONS ----------------------------------------------------#
    def get_users_to_notify(self, transition):
        """Return the appropriate audience to notify for a transition.

        TODO make specific to transition and include email template.
        """
        # result = set()
        # if transition in (STATUS_ACTIVE, STATUS_COMPLETED,
        #        STATUS_TERMINATED, STATUS_SUSPENDED):
        result = set(self.members.all())  # reduce some duplication
        return result

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

    # Project name = "TYPE YEAR-NUMBER TITLE"
    @classmethod
    def clsm_project_type_year_number_name(cls, t, y, n, na):
        """Generate project type - year - number - name."""
        return mark_safe('{0} {1}-{2} {3}'.format(
            Project.PROJECT_ABBREVIATIONS[t], y, str(n).zfill(3), na))

    @property
    def project_type_year_number(self):
        """Return project type - year - number."""
        return Project.clsm_project_type_year_number(
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
    def progressreport(self, year):
        """
        Stub to return the progress report for a given year.

        Instantiate in project classes as appropriate.
        """
        return None

    # -------------------------------------------------------------------------#
    # Team members
    #
    def get_team_list_plain(self):
        """Return a plain text version of the team list."""
        return ", ".join([
            m.user.abbreviated_name for m in
            self.projectmembership_set.select_related('user').all().order_by(
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
        Return a list of lists of project team memberships.

        The list contains:
        * the human-readable role,
        * the team member's full name,
        * the time allocation.
        """
        return[[m.get_role_display(),
                m.user.fullname,
                m.time_allocation] for m in self.projectmembership_set.all()]

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
        verbose_name = _("Science Project")
        verbose_name_plural = _("Science Projects")

    def setup(self):
        """Create a Conceptplan if not already existing."""
        if not self.documents.instance_of(ConceptPlan):
            ConceptPlan.objects.create(
                    project=self,
                    creator=self.creator,
                    modifier=self.modifier)

    @property
    def progressreport(self):
        """
        Return the latest progress report.

        TODO returns the latest progress report, not using the year.
        """
        return self.documents.instance_of(ProgressReport).latest() or None

    def get_progressreport(self, year):
        """Return the ProgressReport for a given year."""
        if not ProgressReport.objects.filter(project=self, year=year).exists():
            a = ARARReport.objects.get(year=year)
            self.make_progressreport(a)
        return ProgressReport.objects.get(project=self, year=year)

    def make_progressreport(self, report):
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
        if (created and
            ProgressReport.objects.filter(
                project=self, year=report.year-1).exists()):
            # This can go wrong:
            p0 = ProgressReport.objects.get(project=self, year=report.year-1)
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
        verbose_name = _("Core Function")
        verbose_name_plural = _("Core Functions")

    def setup(self):
        """A Core Function is now the same as a Science Project. Ah well."""
        ConceptPlan.objects.create(project=self,
                                   creator=self.creator,
                                   modifier=self.modifier)

    @property
    def progressreport(self):
        """Return the latest progress report. Same as ScienceProject.

        TODO returns the latest progress report, not using the year.
        """
        return self.documents.instance_of(ProgressReport).latest() or None

    def get_progressreport(self, year):
        """Return the ProgressReport for a given year."""
        if not ProgressReport.objects.filter(project=self, year=year).exists():
            a = ARARReport.objects.get(year=year)
            self.make_progressreport(a)
        return ProgressReport.objects.get(project=self, year=year)

    def make_progressreport(self, report):
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
        if (created and
            ProgressReport.objects.filter(
                project=self, year=report.year-1).exists()):
            # This can go wrong:
            p0 = ProgressReport.objects.get(project=self, year=report.year-1)
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
        verbose_name = _("External Partnership")
        verbose_name_plural = _("External Partnerships")

    def setup(self):
        """A collaboration project is automatically approved and active."""
        self.status = self.STATUS_ACTIVE
        self.save(update_fields=['status'])

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
    def can_endorse(self):
        return False

    def can_approve(self):
        return False

    def can_request_update(self):
        return False

    def can_request_final_update(self):
        return False

    def can_complete(self):
        return False  # TODO

    def can_terminate(self):
        return False  # TODO

    def can_suspend(self):
        return False  # TODO

    def request_closure(self):
        self.status = Project.STATUS_COMPLETED
        self.save(update_fields=['status'])


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

    LEVELS = (
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
        self.save(update_fields=['status'])

    @transition(field='status',
                verbose_name=_("Request update"),
                save=True,
                source=Project.STATUS_ACTIVE,
                target=Project.STATUS_UPDATE,
                conditions=['can_request_update'])
    def request_update(self, report=None):
        """The Student Report replaces the Progress Report."""
        if report is None:
            report = ARARReport.objects.all().latest()
        self.make_progressreport(report)
        return None

    def can_complete_update(self):
        """The update can be completed when the StudentReport is approved."""
        strep = self.documents.instance_of(StudentReport)
        if strep.count() > 0:
            return strep.latest().is_approved
        else:
            return False

    @transition(field='status',
                verbose_name=_("Request closure"),
                save=True,
                source=Project.STATUS_ACTIVE,
                target=Project.STATUS_COMPLETED,
                conditions=['can_request_closure'],
                permission="submit")
    def request_closure(self):
        """Transition to complete the project. There is no required process."""
        self.status = Project.STATUS_COMPLETED
        self.save(update_fields=['status'])

    # Forbid actions non applicable to this project type
    def can_endorse(self):
        return False

    def can_approve(self):
        return False

    def can_request_final_update(self):
        return False

    def can_complete(self):
        return False

    def can_terminate(self):
        return False

    def can_suspend(self):
        return False

    @property
    def progressreport(self):
        """Return the latest progress report.

        TODO returns the latest progress report, not using the year.
        """
        return self.documents.instance_of(StudentReport).latest() or None

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
        if (created and
            StudentReport.objects.filter(
                project=self, year=report.year-1).exists()):
            p0 = StudentReport.objects.get(project=self, year=report.year-1)
            p.progress_report = p0.progress_report
        p.save()
        msg = "{0} Added StudentReport for year {1} in report {2}".format(
            p.project.project_type_year_number, p.year, p.report)
        logger.debug(msg)
        if settings.DEBUG:
            print(msg)

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
    p = projectmembership_instance.project
    p.team_list_plain = p.get_team_list_plain()
    p.save(update_fields=['team_list_plain'])

    # give user permission to change team?
    # if remove:
    #    print("remove user permission to change or delete team memberships")
    # TODO remove user's permissions on documents
    # else:
    #    print("grant user permission to change or delete team memberships")

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
    from pythia.documents.utils import update_document_permissions
    [update_document_permissions(d) for d in instance.project.documents.all()]
signals.post_save.connect(projectmembership_post_save,
                          sender=ProjectMembership)


def projectmembership_post_delete(sender, instance, using, **kwargs):
    """Post delete hook to refresh cached project membership lists."""
    refresh_project_member_cache_fields(instance, remove=True)
signals.post_delete.connect(projectmembership_post_delete,
                            sender=ProjectMembership)
