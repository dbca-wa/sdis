"""Document models.

Documents have transitions along an approval workflow; some transitions trigger
Project transitions.
"""
from __future__ import (division, print_function, unicode_literals,
                        absolute_import)

from collections import OrderedDict as OD
from datetime import date
from itertools import chain
import logging
import json
from polymorphic import PolymorphicModel, PolymorphicManager

from django.contrib.auth.models import Group
from django.db.models import signals
import django.db.models.options as options
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django_fsm import FSMField, transition

from pythia.models import Audit, ActiveGeoModelManager
from pythia.fields import PythiaArrayField  # , PythiaTextField
from pythia.documents.utils import update_document_permissions
from pythia.reports.models import ARARReport
from pythia.utils import snitch

logger = logging.getLogger(__name__)

BOOL_CHOICES = ((False, _("Incomplete")), (True, _("Complete")))
NULL_CHOICES = ((None, _("Not applicable")), (False, _("Incomplete")),
                (True, _("Complete")))


# Add additional attributes/methods to the model Meta class.
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('display_order',)


def documents_upload_to(instance, filename):
    """Generate a project-specific document upload path."""
    return "documents/{0}-{1}/{2}".format(
        instance.project.year, instance.project.number, filename)


class DocumentManager(PolymorphicManager, ActiveGeoModelManager):
    """
    Custom document manager.

    It seems like a useful API for accessing
    different sorts of documents. It does help some of the template logic.
    """

    @property
    def document_types(self):
        """Find all of our custom document types."""
        document_types = {}
        from django.db.models import get_app, get_models
        app = get_app('documents')
        for model in get_models(app):
            if issubclass(model, self.model) and not model == self.model:
                document_types[model._meta.verbose_name.lower()] = model
        return document_types

    def document_type(self, verbose_name):
        """Return all documents of a particular type."""
        qs = self.get_query_set()
        if verbose_name.lower() in self.document_types.keys():
            return qs.instance_of(self.document_types[verbose_name.lower()])
        else:
            return qs.empty()

    def grouped(self):
        """
        Group the documents into their corresponding document types.

        Ugly hack: To preserve the logical order of document types,
        they are hard-coded here, and documents is an ordered dictionary
        preserving this order.
        """
        documents = OD({})
        document_types = ['concept plan', 'project plan', 'progress report',
                          'student report', 'project closure']

        # for document_type in self.document_types.keys(): # unsorted
        for document_type in document_types:  # sorted
            documents[document_type] = self.document_type(document_type)

        return documents


@python_2_unicode_compatible
class Document(PolymorphicModel, Audit):
    """
    An abstract base class for documents.

    This base class provides completion totals through the ContextStatusMixin.
    """

    STATUS_NEW = 'new'
    STATUS_INREVIEW = 'inreview'
    STATUS_INAPPROVAL = 'inapproval'
    STATUS_APPROVED = 'approved'

    STATUS_CHOICES = (
        (STATUS_NEW, _("New document")),
        (STATUS_INREVIEW, _("Review requested")),
        (STATUS_INAPPROVAL, _("Approval requested")),
        (STATUS_APPROVED, _("Approved"))
        )

    STATUS_LABELS = {
        STATUS_NEW: "danger",
        STATUS_INREVIEW: "warning",
        STATUS_INAPPROVAL: "info",
        STATUS_APPROVED: "success"
        }

    ENDORSEMENT_NOTREQUIRED = 'not required'
    ENDORSEMENT_REQUIRED = 'required'
    ENDORSEMENT_DENIED = 'denied'
    ENDORSEMENT_GRANTED = 'granted'

    ENDORSEMENT_CHOICES = (
        (ENDORSEMENT_REQUIRED, _('required')),
        (ENDORSEMENT_DENIED, _('denied')),
        (ENDORSEMENT_GRANTED, _('granted'))
        )

    ENDORSEMENT_NULL_CHOICES = (
        (ENDORSEMENT_NOTREQUIRED, _('not required')),
        (ENDORSEMENT_REQUIRED, _('required')),
        (ENDORSEMENT_DENIED, _('denied')),
        (ENDORSEMENT_GRANTED, _('granted'))
        )

    template = None
    template_tex = None

    project = models.ForeignKey('projects.Project', related_name='documents')

    status = FSMField(
        default=STATUS_NEW, choices=STATUS_CHOICES,
        verbose_name=_("Document Status"))
    pdf = models.FileField(
            upload_to=documents_upload_to, blank=True, null=True,
            editable=False,
            help_text="The latest, greatest and PDFest version of all times")

    objects = DocumentManager()

    class Meta:
        """Class options."""

        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        get_latest_by = 'created'
        display_order = 0

    @property
    def opts(self):
        """Expose self._meta as property `opts`."""
        return self._meta

    # def save(self, *args, **kwargs):
    #     """Update document permissions on every save."""
    #     # created = True if not self.pk else False
    #
    #     super(Document, self).save(*args, **kwargs)
        # try:
        #     update_document_permissions(self)  # hack: give team access
        # except:
        #     snitch("{0} couldn't update permissions".format(self.__str__()))

        # if created:
        #    self.setup()

    def __str__(self):
        """Return the document type and project type/year/number."""
        from pythia.projects.models import Project
        return mark_safe("{0} {1} {2}-{3:03d}".format(
            self._meta.verbose_name,
            Project.PROJECT_ABBREVIATIONS[self.project.type],
            self.project.year, self.project.number))

    @property
    def debugname(self):
        """Return name and status for use in debug messages."""
        return "{0} ({1})".format(self.__str__(), self.status)

    @property
    def fullname(self):
        """The HTML-safe document name."""
        return mark_safe(self.__str__())

    @property
    def download_title(self):
        """Return the project str() to be used in PDF cover sheets."""
        return self.project.__str__()

    @property
    def download_subtitle(self):
        """Return the document str() to be used in PDF cover sheets."""
        return self.__str__()

    def setup(self):
        """
        Update project members' permissions.

        TODO: do this every time a project membership is added!
        NOTE: permissions are also refreshed on every document save.
        """
        update_document_permissions(self)

    @property
    def status_label(self):
        """Return a human readable document status."""
        return Document.STATUS_LABELS[self.status]

    # -------------------------------------------------------------------------#
    # endorsements
    #
    @property
    def submitter_endorsement_status(self):
        """Return the submitter's endorsement css class and status as string.

        Infers the endorsement status from `self.status`.
        Submitter endorsement is assumed as soon as Document is `submitted for
        review`.
        """
        if self.status == Document.STATUS_NEW:
            return ["label label-danger", Document.ENDORSEMENT_REQUIRED]
        else:
            return ["label label-success", Document.ENDORSEMENT_GRANTED]

    @property
    def reviewer_endorsement_status(self):
        """Return the reviewer's endorsement css class and status as string.

        Infers the endorsement status from `self.status`.
        Reviewer endorsement is assumed as soon as Document is `submitted for
        approval`.
        """
        if self.status in [Document.STATUS_INAPPROVAL,
                           Document.STATUS_APPROVED]:
            return ["label label-success", Document.ENDORSEMENT_GRANTED]
        else:
            return ["label label-danger", Document.ENDORSEMENT_REQUIRED]

    @property
    def approver_endorsement_status(self):
        """Return the approver's endorsement css class and status as string.

        Infers the endorsement status from `self.status`.
        Approver endorsement is assumed as soon as Document is `approved`.
        Would you have guessed?
        """
        if self.status == Document.STATUS_APPROVED:
            return ["label label-success", Document.ENDORSEMENT_GRANTED]
        else:
            return ["label label-danger", Document.ENDORSEMENT_REQUIRED]

    @property
    def endorsements(self):
        """Return endorsements as a list of strings: role, css classes, status.

        Placing this method on the base Document class guarantees that any
        document class has this attribute.

        By default, returns three endorsement roles:

        * Project Team: endorsement given through submitting for review
        * Reviewer: endorsement given through submitting for approval
        * Approver: endorsement given through approving

        For reviewer and approver, the most likely roles `program leader` and
        `directorate` have been used as labels.
        """
        return [
                {
                    "role": "Project Team",
                    "css_classes": self.submitter_endorsement_status[0],
                    "status": self.submitter_endorsement_status[1]
                    },
                {
                    "role": "Program Leader",
                    "css_classes": self.reviewer_endorsement_status[0],
                    "status": self.reviewer_endorsement_status[1]
                    },
                {
                    "role": "Directorate",
                    "css_classes": self.approver_endorsement_status[0],
                    "status": self.approver_endorsement_status[1]
                    },
                ]

    # -------------------------------------------------------------------------#
    # audiences
    #
    @property
    def submitters(self):
        """Return all users with authority to author and "submit" this document.

        Default: project team members.
        """
        return self.project.submitters

    @property
    def reviewers(self):
        """
        Return all users with authority to "review" this document.

        Default: The Program Leaders making up the SCMT.
        """
        return self.project.reviewers

    @property
    def reviewer(self):
        """Return the program leader, who needs to review the document."""
        return self.project.reviewer

    @property
    def approvers(self):
        """
        Return all users with permission to "approve" this document.

        Default: Divisional Directorate members.
        """
        return self.project.approvers

    @property
    def reviewer_approvers(self):
        """Return a deduplicated list of program leader and approvers."""
        return self.project.reviewer_approvers

    @property
    def reviewers_approvers(self):
        """Return a deduplicated list of reviewers, approvers."""
        return self.project.reviewers_approvers

    @property
    def all_involved(self):
        """Return a deduplicated list of submitters, reviewer, approvers.

        This audience is the widest audience to notify.
        """
        return self.project.all_involved

    @property
    def all_permitted(self):
        """Return a deduplicated list of submitters, reviewers, approvers.

        This audience is the widest audience to have write permissions.
        """
        return self.project.all_permitted

    # -------------------------------------------------------------------------#
    # Author actions
    #

    def can_seek_review(self):
        """Return true if this document can be passed to the review stage."""
        return True

    @transition(
        field=status,
        source=STATUS_NEW,
        target=STATUS_INREVIEW,
        conditions=[can_seek_review],
        permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Submit for review",
            explanation=("The Program Leader {0} will review and possibly "
                         "update the document, then either request a revision "
                         "from the project team or submit to the Directorate "
                         "for approval."),
            notify=True,)
        )
    def seek_review(self):
        """Transition this document to being in review."""
        return

    def can_recall(self):
        """Return true if this document can be recalled from review."""
        return True

    @transition(
        field=status,
        source=STATUS_INREVIEW,
        target=STATUS_NEW,
        conditions=[can_recall],
        permission=lambda instance, user: user in instance.submitters,
        custom=dict(verbose="Recall from review",
                    explanation=("The document will be recalled from the "
                                 "Program Leader, made editable to the project"
                                 " team again, who then can submit the"
                                 " document for review again."),
                    notify=True,)
        )
    def recall(self):
        """Transition this document to being new."""
        return

    # -------------------------------------------------------------------------#
    # Reviewer actions
    #
    def can_seek_approval(self):
        """Return true if this document can seek approval."""
        return True

    @transition(
        field=status,
        source=STATUS_INREVIEW,
        target=STATUS_INAPPROVAL,
        conditions=[can_seek_approval],
        permission=lambda instance, user: user in instance.reviewers_approvers,
        custom=dict(
            verbose="Submit for approval",
            explanation=("Submit the document for approval to the "
                         "Directorate."),
            notify=True,)
        )
    def seek_approval(self):
        """Transition this document to be in approval."""

    @transition(
        field=status,
        source=STATUS_INAPPROVAL,
        target=STATUS_INREVIEW,
        conditions=[can_seek_approval],
        permission=lambda instance, user: user in instance.reviewers,
        custom=dict(
            verbose="Recall from approval",
            explanation=("Recall the document from approval by the "
                         "Directorate, e.g. in order to update the content."),
            notify=True,)
        )
    def recall_approval(self):
        """Transition this document from in approval to be in review again."""

    @transition(
        field=status,
        source=STATUS_INREVIEW,
        target=STATUS_NEW,
        conditions=[can_seek_approval],
        permission=lambda instance, user: user in instance.reviewers_approvers,
        custom=dict(
            verbose="Request revision from authors",
            explanation=("Request a substantial revision of the document from "
                         " the project team."),
            notify=True,)
        )
    def request_revision_from_authors(self):
        """Push back to NEW to request a revision from the authors."""
        return

    # -------------------------------------------------------------------------#
    # Approver actions
    #
    def can_approve(self):
        """Return true if this document can be approved."""
        return True

    @transition(
        field=status,
        source=STATUS_INAPPROVAL,
        target=STATUS_APPROVED,
        conditions=[can_approve],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Approve",
            explanation=("Approve the document. This will have consequences"
                         " for the project."),
            notify=True,)
        )
    def approve(self):
        """Approve document."""
        return

    @transition(
        field=status,
        source=STATUS_INAPPROVAL,
        target=STATUS_INREVIEW,
        conditions=[can_approve],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Request reviewer revision",
            explanation=("Request a substantial revision of the document from "
                         " the Program Leader."),
            notify=True,)
        )
    def request_reviewer_revision(self):
        """Push back to INREVIEW to request reviewer revision."""
        return

    @transition(
        field=status,
        source=STATUS_INAPPROVAL,
        target=STATUS_NEW,
        conditions=[can_approve],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Request revision from authors",
            explanation=("Request a substantial revision of the document from "
                         " the project team."),
            notify=True,)
        )
    def request_author_revision(self):
        """Push back to NEW to request author revision."""
        return

    def can_reset(self):
        """Return True if the document can be reset to NEW.

        Since document approval trigger project transitions, resetting the
        approval status of a document should either reset the life cycle of the
        project, or fail due to the project's life cycle.
        """
        return True

    @transition(
        field=status,
        source=STATUS_APPROVED,
        target=STATUS_NEW,
        conditions=[can_reset],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Reset approval status",
            explanation=("Reset the document approval status. "
                         "Revoking this document will have consequences for "
                         "the project."),
            notify=True,)
        )
    def reset(self):
        """Push back to NEW to reset document approval."""

    @property
    def is_draft(self):
        """Return True if the document is NEW."""
        return self.status == self.STATUS_NEW

    @property
    def is_approved(self):
        """Return True if the document is APPROVED."""
        return self.status == self.STATUS_APPROVED

    @property
    def is_nearly_approved(self):
        """Return whether document is in "read-only" mode during approval."""
        return self.status in [self.STATUS_INAPPROVAL, self.STATUS_APPROVED]

    # EMAIL NOTIFICATIONS ----------------------------------------------------#
    def get_users_to_notify(self, target):
        """Return a set of recipients for a given destination status.

        Default: use self.submitters, reviewers and approvers and
        override in Document models
        """
        snitch("Getting recipients for transition target {0}".format(target))
        if target in [Document.STATUS_NEW, Document.STATUS_APPROVED]:
            return self.submitters
        elif target == Document.STATUS_INREVIEW:
            return self.reviewer
        elif target == Document.STATUS_INAPPROVAL:
            return self.approvers
        else:
            return self.submitters

    def get_users_with_change_permissions(self):
        """Return the write-permitted audience for a given status.

        At each status, the directly involved audience plus their line
        management are permitted to change a document.

        * STATUS_NEW: project team + all PLs + Directorate
        * STATUS_INREVIEW: all PLs + Directorate
        * STATUS_INAPPROVAL: Directorate
        * STATUS_APPROVED: None (empty set), but Directorate can reset status
        """
        permitted = set()
        if self.status == Document.STATUS_NEW:
            permitted = self.all_involved
        elif self.status == Document.STATUS_INREVIEW:
            permitted = self.reviewers_approvers
        elif self.status == Document.STATUS_INAPPROVAL:
            permitted = self.approvers
        elif self.status == Document.STATUS_APPROVED:
            permitted = set()

        # snitch("Permitted to change {0}: {1}".format(
        #     self.debugname, ", ".join([p.fullname for p in permitted])))
        return permitted


class ConceptPlan(Document):
    """
    A Science Concept Plan.

    This high-level document is used to scope out a ScienceProject and let the
    Science Management Team determine whether this Project is in line with
    Divisional strategy.

    Modelled after the original document on the DPaW intranet:
    http://intranet/science/Documents/Guideline%207%20Appendix%201%20SCPs.docx
    """

    template = "admin/pythia/ararreport/includes/conceptplan.html"
    template_tex = "latex/includes/conceptplan.tex"

    # summary = PythiaTextField(
    summary = models.TextField(
        verbose_name=_("Background and Aims"), blank=True, null=True,
        help_text=_("Summarise the project in up to 500 words."))
    outcome = models.TextField(
        verbose_name=_("Expected outcome"), blank=True, null=True,
        help_text=_("Summarise the expected outcome in up to 500 words."))
    collaborations = models.TextField(
        verbose_name=_("Expected collaborations"), blank=True, null=True,
        help_text=_("List expected collaborations in up to 500 words."))
    strategic = models.TextField(
        verbose_name=_("Strategic context"), blank=True, null=True,
        help_text=_("Describe the strategic context and management "
                    "implications in up to 500 words."))
    staff = PythiaArrayField(
        verbose_name=_("Staff time allocation"), blank=True, null=True,
        help_text=_("Summarise the staff time allocation by role for the "
                    "first three years, or for a time span appropriate for "
                    "the Project's life time."),
        # default = '<table style="width:400px;" border="1" cellpadding="2">'
        #           '<tbody><tr><td>Role</td><td>Year 1</td><td>Year 2</td>'
        #           '<td>Year 3</td></tr><tr><td>Scientist</td><td></td>'
        #           '<td></td><td></td></tr><tr><td>Technical</td><td>'
        #           '</td><td></td><td></td></tr><tr><td>Volunteer</td>'
        #           '<td></td><td></td><td></td></tr><tr><td>Collaborator</td>'
        #           '<td></td><td></td><td></td></tr></tbody></table>'
        default=json.dumps([
                ['Role', 'Year 1', 'Year 2', 'Year 3'],
                ['Scientist', '', '', ''],
                ['Technical', '', '', ''],
                ['Volunteer', '', '', ''],
                ['Collaborator', '', '', ''],
            ], cls=DjangoJSONEncoder)
        )
    budget = PythiaArrayField(
        verbose_name=_("Indicative operating budget"),
        blank=True, null=True,
        help_text=_("Indicate the operating budget for the first three years, "
                    "or for a time span appropriate for the Project's life "
                    "time."),
        default=json.dumps([
                ['Source', 'Year 1', 'Year 2', 'Year 3'],
                ['Consolidated Funds (DPaW)', '', '', ''],
                ['External Funding', '', '', ''],
            ], cls=DjangoJSONEncoder)
        )
    # Currently not desired:
    director_scd_comment = models.TextField(
        editable=False,  # remove to unhide
        verbose_name=_("Science and Conservation Division Director's Comment"),
        help_text=_("Optional comment to clarify endorsement or provide "
                    "feedback"), blank=True, null=True)
    director_outputprogram_comment = models.TextField(
        editable=False,  # remove to unhide
        verbose_name=_("Comment of the Output Program's Director"),
        help_text=_("Optional comment to clarify endorsement or provide "
                    "feedback"), blank=True, null=True)

    class Meta:
        """Class options."""

        verbose_name = _("Concept Plan")
        verbose_name_plural = _("Concept Plans")
        display_order = 10

    def repair_staff(self):
        """Reset the staff table to its default.

        [doc.repair_staff() for doc in ConceptPlan.objects.filter(staff=None)]
        """
        self.staff = json.dumps([
                ['Role', 'Year 1', 'Year 2', 'Year 3'],
                ['Scientist', '', '', ''],
                ['Technical', '', '', ''],
                ['Volunteer', '', '', ''],
                ['Collaborator', '', '', ''],
            ], cls=DjangoJSONEncoder)
        self.save(update_fields=['staff'])
        logger.info("ConceptPlan {0} field 'staff' reset to default".format(
                    self.__str__()))

    def repair_budget(self):
        """Reset the budget table to its default.

        [doc.repair_budget() for doc in
         ConceptPlan.objects.filter(budget=None)]
        """
        self.budget = json.dumps([
                ['Source', 'Year 1', 'Year 2', 'Year 3'],
                ['Consolidated Funds (DPaW)', '', '', ''],
                ['External Funding', '', '', ''],
            ], cls=DjangoJSONEncoder)
        self.save(update_fields=['budget'])
        logger.info("ConceptPlan {0} field 'budget' reset to default".format(
                    self.__str__()))

    # -------------------------------------------------------------------------#
    # custom transitions and conditions
    #
    def can_seek_review(self):
        """
        Return true if this document can be passed to the review stage.

        Insert here any restrictions (originating from project status etc)
        which could prevent a NEW document from being
        submitted for review by users with permission "submit" (=team).
        """
        # doc permission "submit" restricts seek_review to team already
        return True

    def can_seek_approval(self):
        """
        Return true if this document can seek approval.

        Insert here any restrictions (originating from project status etc)
        which could prevent an INREVIEW document from being
        submitted for approval by users with permission "review" (=SMT).
        """
        # doc permission "review" restricts seek_approval to SMT already
        return True

    # def can_approve(self):
    #     """
    #     Return true if this document can be approved.
    #
    #     Insert here any restrictions (originating from project status etc)
    #     which could prevent an INAPPROVAL document from being approved
    #     by users with the permission "approve".
    #     """
    #     # doc permission "approve" restricts approve to SCD already
    #     return True

    @transition(
        field='status',
        source=Document.STATUS_INAPPROVAL,
        target=Document.STATUS_APPROVED,
        # conditions=[can_approve],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Approve",
            explanation=("Approval of a ConceptPlan signals Directorate "
                         "endorsement for the Project, creates a ProjectPlan, "
                         "which the project team then needs to update and "
                         " submit for review."),
            notify=True,)
        )
    def approve(self):
        """
        Advance the project to status "pending".

        Approving a ConceptPlan will run the actions of Project.endorse(),
        which is to create a ProjectPlan, which the submitters are encouraged
        to update and submit for review.

        We cannot call Project.endorse() here, as the ConceptPlan is not
        approved until the transition finishes.
        We cannot drop the condition "must have approved ConceptPlan" for
        Project.endorse() else Project.endorse() will show up prematurely.
        Another venue might be to use django_fsm.signals.post_transition, if we
        can isolate ConceptPlan.approve from within the signal.
        """
        from pythia.projects.models import Project
        self.project.status = Project.STATUS_PENDING
        self.project.save(update_fields=['status', ])

        pp, created = ProjectPlan.objects.get_or_create(project=self.project)
        pp.save()

    # def can_reset(self):
    #     """Return True if the document can be reset to NEW."""
    #     return True

    @transition(
        field='status',
        source=Document.STATUS_APPROVED,
        target=Document.STATUS_NEW,
        # conditions=[can_reset],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Reset approval status",
            explanation=("Revoking the approval of a ConceptPlan will revoke"
                         " the Directorate's endorsement for the Project. "
                         "The project team will have to revise and re-submit "
                         "the ConceptPlan."),
            notify=True,)
        )
    def reset(self):
        """Reset document approval, reset project status to NEW."""
        from pythia.projects.models import Project
        self.project.status = Project.STATUS_NEW
        self.project.save(update_fields=['status', ])


class ProjectPlan(Document):
    """
    The main project planning document for a Science Project.

    This low-level, detailed document is used to plan out relevance, outcomes,
    communication, data management, knowledge preservation.
    """

    template = "admin/pythia/ararreport/includes/projectplan.html"
    template_tex = "latex/includes/projectplan.tex"

    related_projects = models.TextField(
        verbose_name=_("Related Science Projects"),
        blank=True, null=True,
        editable=True,
        help_text=_("Name related SPPs and the extent you have consulted with "
                    "their project leaders (SPP A6)."))

    # Part C: Relevance and outcomes #
    background = models.TextField(
        verbose_name=_("Background"),
        blank=True, null=True,
        help_text=_("Describe project background (SPP C16) including a "
                    "literature review."))
    aims = models.TextField(
        verbose_name=_("Aims"),
        blank=True, null=True,
        help_text=_("List project aims (SPP C17)."))
    outcome = models.TextField(
        verbose_name=_("Expected outcome"),
        blank=True, null=True,
        help_text=_("Describe expected project outcome."))
    knowledge_transfer = models.TextField(
        verbose_name=_("Knowledge transfer"),
        blank=True, null=True,
        help_text=_("Anticipated users of the knowledge to be gained, and "
                    "technology transfer strategy (SPP C19)."))
    project_tasks = models.TextField(
        verbose_name=_("Tasks and Milestones"),
        blank=True, null=True,
        help_text=_("Major tasks, milestones and outputs (SPP C20). "
                    "Indicate delivery time frame for each task."))
    references = models.TextField(
        verbose_name=_("References"),
        blank=True, null=True,
        help_text=_("Paste in the bibliography of your literature research "
                    "(SPP C21)."))

    # Part D: Study design #
    methodology = models.TextField(
        verbose_name=_("Methodology"),
        blank=True, null=True,
        help_text=_("Describe the study design and statistical analysis"
                    " (SPP D22)."))
    bm_endorsement = models.CharField(
            verbose_name=_("Biometrician's Endorsement"),
            blank=True, null=True,
            max_length=100,
            default=Document.ENDORSEMENT_REQUIRED,
            choices=Document.ENDORSEMENT_CHOICES,
            help_text=_("The Biometrician's endorsement of the methodology's "
                        "statistical validity."))

    # Part E: data management and budget #
    involves_plants = models.BooleanField(
        verbose_name=_("Involves plant specimen collection"),
        blank=False, null=False,
        default=False,
        help_text=_("Tick to indicate that this project will collect plant "
                    "specimens, which will require endorsement by the "
                    "Herbarium Curator."))
    no_specimens = models.TextField(
        verbose_name=_("No. specimens"),
        blank=True, null=True,
        help_text=_("Estimate the number of collected vouchered specimens "
                    "(SPP E23). Provide any additional info required for "
                    "the Harbarium Curator's endorsement."))
    hc_endorsement = models.CharField(
            verbose_name=_("Herbarium Curator's Endorsement"),
            blank=True, null=True,
            max_length=100,
            default=Document.ENDORSEMENT_NOTREQUIRED,
            choices=Document.ENDORSEMENT_NULL_CHOICES,
            help_text=_("The Herbarium Curator's endorsement of the planned "
                        "collection of voucher specimens."))

    # New one! Animal Ethics Committee approval
    involves_animals = models.BooleanField(
        verbose_name=_("Involves interaction with vertebrate animals"
                       " (excl. fish)"),
        blank=False, null=False,
        default=False,
        help_text=_("Tick to indicate that this project will involve "
                    "direct interaction with animals, which will require "
                    "endorsement by the Animal Ethics Committee."))
    ae_endorsement = models.CharField(
            verbose_name=_("Animal Ethics Committee's Endorsement"),
            blank=True, null=True,
            max_length=100,
            default=Document.ENDORSEMENT_NOTREQUIRED,
            choices=Document.ENDORSEMENT_NULL_CHOICES,
            help_text=_("The Animal Ethics Committee's endorsement of the"
                        " planned direct interaction with animals. "
                        "Approval process is currently handled outside "
                        "of SDIS."))

    data_management = models.TextField(
        verbose_name=_("Data management"), blank=True, null=True,
        help_text=_("Describe how and where data will be maintained, archived,"
                    " cataloged (SPP E24). Read DPaW guideline 16."))
    # Data manager's endorsement!!!
    data_manager_endorsement = models.CharField(
            editable=False,  # uncomment to unleash data management goodness
            verbose_name=_("Data Manager's Endorsement"),
            blank=True, null=True,
            max_length=100,
            choices=Document.ENDORSEMENT_NULL_CHOICES,
            help_text=_("The Data Manager's endorsement of the project's "
                        "data management. The DM will help to set up Wiki"
                        "pages, data catalogue permissions, scientific sites, "
                        "and advise on metadata creation."))

    operating_budget = PythiaArrayField(
        verbose_name=_("Consolidated Funds"),
        blank=True, null=True,
        help_text=_("Estimated budget: consolidated DPaW funds"),
        default=json.dumps([
                ['Source', 'Year 1', 'Year 2', 'Year 3'],
                ['FTE Scientist', '', '', ''],
                ['FTE Technical', '', '', ''],
                ['Equipment', '', '', ''],
                ['Vehicle', '', '', ''],
                ['Travel', '', '', ''],
                ['Other', '', '', ''],
                ['Total', '', '', ''],
            ], cls=DjangoJSONEncoder))

    operating_budget_external = PythiaArrayField(
        verbose_name=_("External Funds"), blank=True, null=True,
        help_text=_("Estimated budget: external funds"),
        default=json.dumps([
                ['Source', 'Year 1', 'Year 2', 'Year 3'],
                ['Salaries, Wages, Overtime', '', '', ''],
                ['Overheads', '', '', ''],
                ['Equipment', '', '', ''],
                ['Vehicle', '', '', ''],
                ['Travel', '', '', ''],
                ['Other', '', '', ''],
                ['Total', '', '', ''],
            ], cls=DjangoJSONEncoder))

    class Meta:
        """Class options."""

        verbose_name = _("Project Plan")
        verbose_name_plural = _("Project Plans")
        display_order = 20

    def repair_operating_budget(self):
        """Reset the operating budget to its default.

        [p.repair_operating_budget() for p in
         ProjectPlan.objects.filter(operating_budget=None)]
        """
        self.operating_budget = json.dumps([
                ['Source', 'Year 1', 'Year 2', 'Year 3'],
                ['FTE Scientist', '', '', ''],
                ['FTE Technical', '', '', ''],
                ['Equipment', '', '', ''],
                ['Vehicle', '', '', ''],
                ['Travel', '', '', ''],
                ['Other', '', '', ''],
                ['Total', '', '', ''],
            ], cls=DjangoJSONEncoder)
        self.save(update_fields=['operating_budget'])
        logger.info("ProjectPlan {0}".format(self.__str__()) +
                    " field 'operating_budget' reset to default")

    def repair_operating_budget_external(self):
        """Reset the external operating budget to its default.

        [p.repair_operating_budget_external() for p in
         ProjectPlan.objects.filter(operating_budget_external=None)]
        """
        self.operating_budget_external = json.dumps([
                ['Source', 'Year 1', 'Year 2', 'Year 3'],
                ['Salaries, Wages, Overtime', '', '', ''],
                ['Overheads', '', '', ''],
                ['Equipment', '', '', ''],
                ['Vehicle', '', '', ''],
                ['Travel', '', '', ''],
                ['Other', '', '', ''],
                ['Total', '', '', ''],
            ], cls=DjangoJSONEncoder)
        self.save(update_fields=['operating_budget_external'])
        logger.info("ProjectPlan {0}".format(self.__str__()) +
                    "field 'operating_budget_external' reset to default")

    # -------------------------------------------------------------------------#
    # custom transitions and conditions
    #

    def can_seek_review(self):
        """
        Whether this document can be passed to the review stage.

        Insert here any restrictions (originating from project status etc)
        which could prevent a NEW document from being
        submitted for review by users with permission "submit" (=team).
        """
        # doc permission "submit" restricts seek_review to team already
        return True

    @property
    def cleared_bm(self):
        """Whether BM endorsement has been granted.

        Recipient of endorsement request: Biometrician(s)
        Group.objects.get(name='BM').user_set.all()
        """
        return self.bm_endorsement == Document.ENDORSEMENT_GRANTED

    @property
    def cleared_dm(self):
        """Whether Data manager endorsement has been granted.

        Recipient of endorsement request: Data Manager(s)
        self.project.program.data_custodian
        """
        return self.dm_endorsement == Document.ENDORSEMENT_GRANTED

    @property
    def cleared_hc(self):
        """Whether HC endorsement is required and granted or not required.

        Recipient of endorsement request: Herbarium Custodian(s)
        Group.objects.get(name='HC').user_set.all()
        """
        if self.involves_plants:
            return self.hc_endorsement == Document.ENDORSEMENT_GRANTED
        else:
            # no plants, no endorsement, all good
            return True

    @property
    def cleared_ae(self):
        """Whether HC endorsement is required and granted, or not required.

        Recipient of endorsement request:
        Animal Ethics Committee representative(s)
        Group.objects.get(name='AE').user_set.all()
        """
        if self.involves_animals:
            return self.ae_endorsement == Document.ENDORSEMENT_GRANTED
        else:
            # no animals, no endorsement, all good
            return True

    # Custom reviewer audience includes special roles ------------------------#
    @property
    def reviewer(self):
        """Return document reviewers PL, BM, plus if neede AE and HC."""
        bm = Group.objects.get_or_create(name='BM')[0].user_set.all()
        ae = Group.objects.get_or_create(name='AE')[0].user_set.all()
        hc = Group.objects.get_or_create(name='HC')[0].user_set.all()
        AE = ae if not self.cleared_ae else set()
        HC = hc if not self.cleared_hc else set()
        reviewers = list(set(chain(self.project.reviewer, bm, AE, HC)))

        return reviewers

    # ------------------------------------------------------------------------#
    # custom endorsements

    @property
    def bm_endorsement_status(self):
        """The biometrician's endorsement css class and status as string.

        Determines the endorsement status from property cleared_bm.
        """
        if self.cleared_bm:
            return ["label label-success", Document.ENDORSEMENT_GRANTED]
        else:
            return ["label label-danger", Document.ENDORSEMENT_REQUIRED]

    @property
    def dm_endorsement_status(self):
        """The data manager's endorsement css class and status as string.

        Determines the endorsement status from property `cleared_dm`.
        """
        if self.cleared_dm:
            return ["label label-success", Document.ENDORSEMENT_GRANTED]
        else:
            return ["label label-danger", Document.ENDORSEMENT_REQUIRED]

    @property
    def hc_endorsement_status(self):
        """The herbarium curator's endorsement css class and status as string.

        Determines the endorsement status from property `cleared_hc`.
        """
        if not self.involves_plants:
            return ["label label-default", Document.ENDORSEMENT_NOTREQUIRED]
        else:
            if self.cleared_hc:
                return ["label label-success", Document.ENDORSEMENT_GRANTED]
            else:
                return ["label label-danger", Document.ENDORSEMENT_REQUIRED]

    @property
    def ae_endorsement_status(self):
        """The animal ethics committee's endorsement css class and status as string.

        Determines the endorsement status from property `cleared_ae`.
        """
        if not self.involves_animals:
            return ["label label-default", Document.ENDORSEMENT_NOTREQUIRED]
        else:
            if self.cleared_ae:
                return ["label label-success", Document.ENDORSEMENT_GRANTED]
            else:
                return ["label label-danger", Document.ENDORSEMENT_REQUIRED]

    @property
    def endorsements(self):
        """Return a dictionary of document endorsements.

        The dict contains three keys:
        * role: the human-readable role of the endorser,
        * css_classes: the CSS classes to render the endorsement label,
        * status: the human-readable status of the endorsement.

        Endorsers are the Biometrician, the Herbarium Curator, the Animal
        Ethics Committee, and soon, the Data Manager.
        """
        return super(ProjectPlan, self).endorsements + [
                {
                    "role": "Biometrician",
                    "css_classes": self.bm_endorsement_status[0],
                    "status": self.bm_endorsement_status[1]
                    },
                # {
                # "role": "Data Manager",
                # "css_classes": self.dm_endorsement_status[0],
                # "status": self.dm_endorsement_status[1]
                #   },
                {
                    "role": "Herbarium Curator",
                    "css_classes": self.hc_endorsement_status[0],
                    "status": self.hc_endorsement_status[1]
                    },
                {
                    "role": "Animal Ethics Committee",
                    "css_classes": self.ae_endorsement_status[0],
                    "status": self.ae_endorsement_status[1]
                    }
                ]

    def can_seek_approval(self):
        """
        Return true if this document can seek approval.

        Insert here any restrictions (originating from project status etc)
        which could prevent an INREVIEW document from being
        submitted for approval by users with permission "review" (=SMT, PL).

        Gate check for endorsements: Biometrician mandatory, Herbarium optional

        Permission "review" restricts seek_approval to SMT already
        """
        return self.cleared_bm and self.cleared_hc

    def can_approve(self):
        """
        Return true if this document can be approved.

        Insert here any restrictions (originating from project status etc)
        which could prevent an INAPPROVAL document from being approved
        by users with the permission "approve".

        Gate check for endorsements: AEC only if required.
        """
        # doc permission "approve" restricts approve to SCD already
        return self.cleared_ae

    @transition(
        field='status',
        source=Document.STATUS_INAPPROVAL,
        target=Document.STATUS_APPROVED,
        conditions=[can_approve],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Approve",
            explanation=("Approving the ProjectPlan activates the Project."
                         "This means that formal work on the Project may "
                         "commence, and annual updates will be required."),
            notify=True,)
        )
    def approve(self):
        """Approve document and turn project active."""
        from pythia.projects.models import Project
        self.project.status = Project.STATUS_ACTIVE
        self.project.save(update_fields=['status', ])

    @transition(
        field='status',
        source=Document.STATUS_APPROVED,
        target=Document.STATUS_NEW,
        # conditions=[can_reset],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Reset approval status",
            explanation=("Revoking the approval of a ProjectPlan will "
                         "push the Project back to being in the planning "
                         "phase. The Project team will have to submit a"
                         "revised ProjectPlan."),
            notify=True,)
        )
    def reset(self):
        """Resetting ProjectPlan approval pushes Project to PENDING."""
        from pythia.projects.models import Project
        self.project.status = Project.STATUS_PENDING
        self.project.save(update_fields=['status', ])


def projectplan_post_save(sender, instance, created, **kwargs):
    """Post-save: Set optional endorsements based on other fields.

    If the project owner indicates that the project will involve
    plant specimen collection or animal interaction,
    the respective endorsement from Herbarium Curator (HC) or
    Animal Ethics Committee (AE) will be set to "requested".

    NB: the mandatory Biometrician's endorsement defaults to "requested".
    Data manager's endorsement will do the same once activated.
    """
    snitch('ProjectPlan {0} post-save: setting required endorsements '
           'as inferred from other fields.'.format(instance.__str__()))
    if instance.involves_plants:
        snitch('Project involves plants, needs HC endorsement!')
        if instance.hc_endorsement == Document.ENDORSEMENT_NOTREQUIRED:
            snitch('Setting HC endorsement from default to "required".')
            instance.hc_endorsement = Document.ENDORSEMENT_REQUIRED
            instance.save(update_fields=['hc_endorsement'])

    if instance.involves_animals:
        snitch('Project involves animals, needs AE endorsement!')
        if instance.ae_endorsement == Document.ENDORSEMENT_NOTREQUIRED:
            snitch('Setting AE endorsement from default to "required".')
            instance.ae_endorsement = Document.ENDORSEMENT_REQUIRED
            instance.save(update_fields=['ae_endorsement'])

signals.post_save.connect(projectplan_post_save, sender=ProjectPlan)


class ProgressReport(Document):
    """
    An annual Progress Report on Science Projects and Core Functions.

    This report is mainly used in SCD's Annual Research Activity Report (ARAR).
    """

    template = "admin/pythia/ararreport/includes/progressreport.html"
    template_tex = "latex/includes/progressreport.tex"

    is_final_report = models.BooleanField(
        verbose_name=_("Is final report"),
        default=False, editable=False,
        help_text=_("Whether this report is the final progress report "
                    "after submitting a project closure request."))
    year = models.PositiveIntegerField(
        verbose_name=_("Report year"),
        editable=False,
        default=lambda: date.today().year,
        help_text=_("The year on which this progress report reports on "
                    "with four digits, e.g. 2014 for FY 2013/14."))
    report = models.ForeignKey(
        ARARReport,
        blank=True, null=True,
        editable=False,
        help_text=_("The annual report publishing this StudentReport"))
    context = models.TextField(
        verbose_name=_("Context"),
        blank=True, null=True,
        help_text=_("A shortened introduction / background for the annual "
                    "activity update. Aim for 100 to 150 words."))
    aims = models.TextField(
        verbose_name=_("Aims"),
        blank=True, null=True,
        help_text=_("A bullet point list of aims for the annual activity "
                    "update. Aim for 100 to 150 words. One bullet point per "
                    "aim."))
    progress = models.TextField(
        verbose_name=_("Progress"),
        blank=True, null=True,
        help_text=_("Current progress and achievements for the annual "
                    "activity update. Aim for 100 to 150 words. One bullet "
                    "point per achievement."))
    implications = models.TextField(
        verbose_name=_("Management implications"),
        blank=True, null=True,
        help_text=_("Management implications for the annual activity update. "
                    "Aim for 100 to 150 words. One bullet point per "
                    "implication."))
    future = models.TextField(
        verbose_name='Future directions',
        blank=True, null=True,
        help_text=_("Future directions for the annual activity update. Aim "
                    "for 100 to 150 words. One bullet point per direction."))

    class Meta:
        """Class options."""

        verbose_name = _("Progress Report")
        verbose_name_plural = _("Progress Reports")
        # unique_together = (("year", "project"))
        display_order = 30

    def __str__(self):
        """The name including reporting period."""
        from pythia.projects.models import Project
        return "Progress Report {0} {1}-{2:03d} (FY {3}-{4})".format(
            Project.PROJECT_ABBREVIATIONS[self.project.type],
            self.project.year,
            self.project.number,
            str(self.year-1),
            str(self.year))

    # def can_seek_review(self):
    #     """
    #     Return true if this document can be passed to the review stage.
    #
    #     Insert here any restrictions (originating from project status etc)
    #     which could prevent a NEW document from being
    #     submitted for review by users with permission "submit" (=team).
    #     """
    #     # doc permission "submit" restricts seek_review to team already
    #     return True

    # def can_seek_approval(self):
    #     """
    #     Return true if this document can seek approval.
    #
    #     Insert here any restrictions (originating from project status etc)
    #     which could prevent an INREVIEW document from being
    #     submitted for approval by users with permission "review" (=SMT).
    #     """
    #     # doc permission "review" restricts seek_approval to SMT already
    #     return True

    # def can_approve(self):
    #     """
    #     Return true if this document can be approved.
    #
    #     Insert here any restrictions (originating from project status etc)
    #     which could prevent an INAPPROVAL document from being approved
    #     by users with the permission "approve".
    #     """
    #     # doc permission "approve" restricts approve to SCD already
    #     return True

    @transition(
        field='status',
        source=Document.STATUS_INAPPROVAL,
        target=Document.STATUS_APPROVED,
        # conditions=[can_approve],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Approve",
            explanation=("Approving a ProgressReport will complete the annual "
                         "update and bring the Project back to its normal, "
                         "active state, or complete an ongoing closure "
                         "process."),
            notify=True,)
        )
    def approve(self):
        """Complete the requested update.

        This will set the document status to APPROVED and call the appropriate
        project transition:

        * projects in Project.STATUS_UPDATE will transition back to
          `Project.STATUS_ACTIVE`;
        * projects in `Project.STATUS_FINAL_UPDATE` will transition forward to
          `Project.STATUS_COMPLETED`.
        """
        from pythia.projects.models import Project
        if self.project.status == Project.STATUS_UPDATE:
            self.project.status = Project.STATUS_ACTIVE
        elif self.project.status == Project.STATUS_FINAL_UPDATE:
            self.project.status = Project.STATUS_COMPLETED
        self.project.save(update_fields=['status', ])

    @transition(
        field='status',
        source=Document.STATUS_APPROVED,
        target=Document.STATUS_NEW,
        # conditions=[can_reset],  # needs def can_reset() here
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Reset approval status",
            explanation=("Revoking the approval of a ProgressReport will "
                         "restart its annual update process."),
            notify=True,)
        )
    def reset(self):
        """Push the project back to status before ProgressReport approval."""
        from pythia.projects.models import Project
        if self.project.status == Project.STATUS_ACTIVE:
            self.project.status = Project.STATUS_UPDATE
        elif self.project.status == Project.STATUS_COMPLETED:
            self.project.status = Project.STATUS_FINAL_UPDATE
        self.project.save(update_fields=['status', ])


class ProjectClosure(Document):
    """
    The required documentation to apply for project closure.

    Authors fill in closure form.
    SMT reviews and approves.
    On last Progress Report approval, after ARAR publication, Project status
    changes to completed, suspended or terminated.
    """

    template = "admin/pythia/ararreport/includes/projectclosure.html"
    template_tex = "latex/includes/projectclosure.tex"
    STATUS_COMPLETED = 'completed'
    STATUS_FORCE_COMPLETED = 'force_completed'
    STATUS_TERMINATED = 'terminated'
    STATUS_SUSPENDED = 'suspended'

    GOAL_CHOICES = (
        (STATUS_COMPLETED, _("Completed with final update")),
        (STATUS_FORCE_COMPLETED, _("Completed without final update")),
        (STATUS_SUSPENDED, _("Suspended")),
        (STATUS_TERMINATED, _("Terminated"))
        )

    goal = models.CharField(
        max_length=300,
        verbose_name=_("Closure goal"),
        blank=True, null=True,
        default=STATUS_COMPLETED,
        choices=GOAL_CHOICES,
        help_text=_("The intended project status outcome of this closure."))
    reason = models.TextField(
        verbose_name=_("Closure reason"),
        blank=True, null=True,
        help_text=_("Reason for closure, provided by project team and/or"
                    " program leader."))
    scientific_outputs = models.TextField(
        verbose_name=_("Key publications and documents"),
        blank=True, null=True,
        help_text=_("List key publications and documents."))
    knowledge_transfer = models.TextField(
        verbose_name=_("Knowledge Transfer"),
        blank=True, null=True,
        help_text=_("List knowledge transfer achievements."))
    data_location = models.TextField(
        verbose_name=_("Dataset links"),
        blank=True, null=True,
        help_text=_("Paste links to all datasets of this project on the "
                    "<a target=\"_\" href=\"http://internal-data.dpaw.wa."
                    "gov.au/\">data catalogue</a>."))
    hardcopy_location = models.TextField(
        verbose_name=_("Hardcopy location"),
        blank=True, null=True,
        help_text=_("Location of hardcopy of all project data."))
    backup_location = models.TextField(
        verbose_name=_("Backup location"),
        blank=True, null=True,
        editable=False,
        help_text=_("Location of electronic project data."))

    class Meta:
        """Class options."""

        verbose_name = _("Project Closure")
        verbose_name_plural = _("Project Closures")
        display_order = 50

    @transition(
        field='status',
        source=Document.STATUS_INAPPROVAL,
        target=Document.STATUS_APPROVED,
        # conditions=[can_approve],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Approve",
            explanation=("Approving a ClosureForm will make the Project "
                         "await its last annual update before the closure "
                         "process is complete."),
            notify=True,)
        )
    def approve(self):
        """Auto-advance the project to CLOSING stated depending on goal.

        * Approving force complete will complete the project immediately.
        * Approving suspension or termination will suspend or terminate the
        project immediately.
        * All other cases (failsafe! there's only refular completion left) will
        set the project to pending final update.
        """
        from pythia.projects.models import Project
        if self.goal == ProjectClosure.STATUS_FORCE_COMPLETED:
            self.project.status = Project.STATUS_COMPLETED
        elif self.goal == ProjectClosure.STATUS_TERMINATED:
            self.project.status = Project.STATUS_TERMINATED
        elif self.goal == ProjectClosure.STATUS_SUSPENDED:
            self.project.status = Project.STATUS_SUSPENDED
        else:
            self.project.status = Project.STATUS_CLOSING
        self.project.save(update_fields=['status', ])

    @transition(
        field='status',
        source=Document.STATUS_APPROVED,
        target=Document.STATUS_NEW,
        # conditions=[can_reset],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Reset approval status",
            explanation=("Revoking the approval of a ProjectClosure pushes "
                         "the Project back to its active state."),
            notify=True,)
        )
    def reset(self):
        """Revoke document approval transitions project back to active."""
        from pythia.projects.models import Project
        self.project.status = Project.STATUS_ACTIVE
        self.project.save(update_fields=['status', ])


@python_2_unicode_compatible
class StudentReport(Document):
    """A progress report for Student Projects."""

    template = "admin/pythia/ararreport/includes/studentreport.html"
    template_tex = "latex/includes/studentreport.tex"

    year = models.PositiveIntegerField(
        verbose_name=_("Report year"),
        editable=False,
        default=lambda: date.today().year,
        help_text=_("The year on which this progress report reports on "
                    "with four digits, e.g. 2014"))
    progress_report = models.TextField(
        verbose_name=_("Progress Report"),
        blank=True, null=True,
        help_text=_("Report the Progress in max. 150 words."))
    report = models.ForeignKey(
        ARARReport,
        blank=True, null=True,
        editable=False,
        help_text=_("The annual report publishing this StudentReport"))

    class Meta:
        """Class options."""

        verbose_name = _("Student Report")
        verbose_name_plural = _("Student Reports")
        display_order = 40

    def __str__(self):
        """The name including reporting period."""
        from pythia.projects.models import Project
        return "Progress Report {0} {1}-{2:03d} (FY {3}-{4})".format(
            Project.PROJECT_ABBREVIATIONS[self.project.type],
            self.project.year,
            self.project.number,
            str(self.year-1),
            str(self.year))

    @transition(
        field='status',
        source=Document.STATUS_INAPPROVAL,
        target=Document.STATUS_APPROVED,
        # conditions=[can_approve],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Approve",
            explanation=("Approving a StudentReport completes the annual "
                         "update and brings the Project back to its normal, "
                         "active state."),
            notify=True,)
        )
    def approve(self):
        """Approving the update transitions project back to active."""
        from pythia.projects.models import Project
        self.project.status = Project.STATUS_ACTIVE
        self.project.save(update_fields=['status', ])

    @transition(
        field='status',
        source=Document.STATUS_APPROVED,
        target=Document.STATUS_NEW,
        # conditions=[can_reset],
        permission=lambda instance, user: user in instance.approvers,
        custom=dict(
            verbose="Reset approval status",
            explanation=("Revoking the approval of a StudentReport will "
                         "restart the annual update. The project team "
                         "will have to submit a revised StudentReport "
                         "to complete the update."),
            notify=True,)
        )
    def reset(self):
        """
        Push back to NEW to reset document approval.

        Project status hard-reset to STATUS_UPDATE (no tx).
        """
        from pythia.projects.models import Project
        self.project.status = Project.STATUS_UPDATE
        self.project.save(update_fields=['status', ])


class StaffTimeEstimate(Audit):
    """
    An estimate of staff time (role or names) for three years, unused.

    Equals one row in the ConceptPlan's 'Staff time allocation' table.
    """

    ROLE_SUPERVISING_SCIENTIST = 1
    ROLE_RESEARCH_SCIENTIST = 2
    ROLE_TECHNICAL_OFFICER = 3
    ROLE_EXTERNAL_COLLABORATOR = 9
    ROLE_OTHER = 10

    ROLE_CHOICES = (
        (ROLE_SUPERVISING_SCIENTIST, "Supervising Scientist"),
        (ROLE_RESEARCH_SCIENTIST, "Research Scientist"),
        (ROLE_TECHNICAL_OFFICER, "Technical Officer"),
        (ROLE_EXTERNAL_COLLABORATOR, "External Collaborator"),
        (ROLE_OTHER, "Other (specify)"),
        )
    document = models.ForeignKey(
        ConceptPlan, help_text=_("The Concept Plan."))
    role = models.TextField(
        verbose_name=_("Role"), blank=True, null=True,
        choices=ROLE_CHOICES,
        help_text=_("The role of the involved staff."))
    staff = models.TextField(
        verbose_name=_("Staff"), blank=True, null=True,
        help_text=_("The involved staff if known."))
    year1 = models.TextField(
        verbose_name=_("Year 1"), blank=True, null=True,
        help_text=_("The time allocation in year 1 of the project in FTE."))
    year2 = models.TextField(
        verbose_name=_("Year 2"), blank=True, null=True,
        help_text=_("The time allocation in year 2 of the project in FTE."))
    year3 = models.TextField(
        verbose_name=_("Year 3"), blank=True, null=True,
        help_text=_("The time allocation in year 3 of the project in FTE."))
