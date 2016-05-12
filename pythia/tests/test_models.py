"""Model tests for SDIS."""
from django.test import TestCase
from django.contrib.auth.models import Group
# from django_fsm.db.fields import TransitionNotAllowed

from pythia.models import Program
from pythia.documents.models import (
    Document, StudentReport, ConceptPlan, ProjectPlan, ProgressReport)
from pythia.projects.models import (Project, ProjectMembership)
from pythia.reports.models import ARARReport
from .base import (BaseTestCase, ProjectFactory, ScienceProjectFactory,
                   CoreFunctionProjectFactory, CollaborationProjectFactory,
                   StudentProjectFactory, UserFactory, SuperUserFactory)


def avail_tx(user, tx, obj):
    """Return whether a user has transition tx available on an obj."""
    return tx in [t.name for t in
                  obj.get_available_user_status_transitions(user)]


class UserModelTests(TestCase):
    """User model tests."""

    def test_user_is_valid_with_email_only(self):
        """Test that a user profile is valid with an email only.

        A user profile must be valid with an email only.
        Everything else is a bonus!
        """
        print("TODO")
        pass  # TODO


class ProjectModelTests(BaseTestCase):
    """Base project tests."""

    def test_creation_adds_project_membership(self):
        """The sup scientist is added to the team on project creation."""
        project = ProjectFactory.create()
        self.assertEqual(ProjectMembership.objects.count(), 1)
        membership = ProjectMembership.objects.all()[0]
        self.assertEqual(project.project_owner, membership.user)
        self.assertEqual(membership.role,
                         ProjectMembership.ROLE_SUPERVISING_SCIENTIST)
        self.assertEqual(membership.project, project)


class ScienceProjectModelTests(BaseTestCase):
    """Tests along the life cycle of a ScienceProject.

    Special attention is paid to user groups, permissions, transitions,
    documents, project status.
    """

    def setUp(self):
        """Create a ScienceProject and users for all roles.

        * user: a superuser
        * smt: reviewer group
        * scd: approver group
        * bob bobson: Bob, a research scientist, wants to create a new
            science project. Bob will be the principal scientist of that
            project, add team members, write project documentation,
            submit docs for approval, and write updates.
        * John Johnson: John will join Bob's team. Then he should be able
            to execute "team-only" submit actions.
        * Steven Stevenson: Steven is Bob's Program Leader.
            As a member of SMT, the reviewers, Steven is the first instance of
            approval.
        * Marge Simpson: Marge is the Divisional Director.
            As member of the Directorate, M is the highest instance of approval
            and has resurrection powers for projects.
        * Fran Franson, another PL and member of SMT, is also a reviewer.
        * Peter Peterson: Peter won't have anything to do with the project.
            Peter should not be able to execute any "team-only" actions!
        """
        self.smt, created = Group.objects.get_or_create(name='SMT')
        self.scd, created = Group.objects.get_or_create(name='SCD')
        self.users, created = Group.objects.get_or_create(name='Users')

        self.superuser = SuperUserFactory.create(username='admin')
        self.bob = UserFactory.create(
            username='bob', first_name='Bob', last_name='Bobson')
        self.john = UserFactory.create(
            username='john', first_name='John', last_name='Johnson')
        self.steven = UserFactory.create(
            username='steven', first_name='Steven', last_name='Stevenson')
        self.steven.groups.add(self.smt)
        self.marge = UserFactory.create(
            username='marge', first_name='Marge', last_name='Simpson')
        self.marge.groups.add(self.scd)
        self.peter = UserFactory.create(
            username='peter', first_name='Peter', last_name='Peterson')

        self.program = Program.objects.create(
                name="ScienceProgram",
                slug="scienceprogram",
                position=0,
                program_leader=self.steven)

        self.project = ScienceProjectFactory.create(
            creator=self.bob,
            modifier=self.bob,
            program=self.program,
            # data_custodian=self.bob, site_custodian=self.bob,
            project_owner=self.bob)

        ProjectMembership.objects.create(
            project=self.project,
            user=self.bob,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        self.scp = self.project.documents.instance_of(ConceptPlan).get()

    def test_new_science_project(self):
        """A new ScienceProject has one new ConceptPlan and only setup tx."""
        p = self.project

        print("A new ScienceProject must be of STATUS_NEW.")
        self.assertEqual(p.status, Project.STATUS_NEW)

        print("A new SP has exactly one document, a ConceptPlan.")
        self.assertEqual(p.documents.count(), 1)
        self.assertEqual(p.documents.instance_of(ConceptPlan).count(), 1)

        print("A new SP has only setup tx until the SCP is approved.")
        avail_tx = [t.name for t in p.get_available_status_transitions()]
        self.assertEqual(len(avail_tx), 1)
        self.assertTrue('setup' in avail_tx)

        print("A project cannot be endorsed without an approved ConceptPlan.")
        self.assertFalse(p.can_endorse())

    def test_conceptplan_permissions(self):
        """Test expected ConceptPlan permissions.

        * All users should be able to view.
        * Only project team members should be able to change and submit.
        * Only SMT members should be able to review.
        * Only SCD members should be able to approve.
        """
        print("Only project team members like Bob can submit the ConceptPlan.")
        self.assertTrue(avail_tx(self.bob, 'seek_review', self.scp))

        print("John is not on the team and has no permission to submit.")
        self.assertFalse(avail_tx(self.john, 'seek_review', self.scp))

        print("Peter is not on the team and has no permission to submit.")
        self.assertFalse(avail_tx(self.peter, 'seek_review', self.scp))

        print("John joins the project team.")
        ProjectMembership.objects.create(
            project=self.project,
            user=self.john,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        print("John is now on the team and has permission to submit.")
        self.assertTrue(avail_tx(self.john, 'seek_review', self.scp))

        # print("Only Program Leaders (reviewers) can review.")
        # scp_review = 'documents.review_conceptplan'
        # self.assertTrue(self.steven.has_perm(scp_review))
        # self.assertFalse(self.bob.has_perm(scp_review))

        # print("Only Directorate (approvers) can approve.")
        # scp_approve = 'documents.approve_conceptplan'
        # self.assertTrue(self.marge.has_perm(scp_approve))
        # self.assertFalse(self.steven.has_perm(scp_approve))
        # self.assertFalse(self.bob.has_perm(scp_approve))

        # print("Everyone can update a project.")
        # pro_change = 'projects.change_scienceproject'
        # self.assertTrue(self.steven.has_perm(pro_change))
        # self.assertTrue(self.bob.has_perm(pro_change))
        # self.assertTrue(self.john.has_perm(pro_change))

        # print("Everyone can update a document.")
        # scp_change = 'documents.change_conceptplan'
        # self.assertTrue(self.steven.has_perm(scp_change))
        # self.assertTrue(self.bob.has_perm(scp_change))
        # self.assertTrue(self.john.has_perm(scp_change))
        # self.assertTrue(self.peter.has_perm(scp_change))

    def test_scienceproject_lifecycle(self):
        """Test all possible transitions in a ScienceProject's life cycle.

        Focus on objects being created, gate checks.
        Ignoring user permissions.
        """
        p = self.project
        scp = p.documents.instance_of(ConceptPlan).get()

        print("The ConceptPlan is new and ready to be submitted.")
        self.assertTrue(scp.status == Document.STATUS_NEW)
        self.assertTrue(scp.can_seek_review())

        print("The team submits for review")
        scp.seek_review()
        # The SCP sits with the Program Leader now
        self.assertTrue(scp.status == Document.STATUS_INREVIEW)
        self.assertTrue(scp.can_seek_approval())

        print("The team recalls the document from review.")
        scp.recall()
        self.assertTrue(scp.status == Document.STATUS_NEW)

        print("The team re-submits the doc for review.")
        scp.seek_review()
        self.assertTrue(scp.status == Document.STATUS_INREVIEW)
        self.assertTrue(scp.can_seek_approval())

        print("The reviewer request revision from authors.")
        scp.request_revision_from_authors()
        self.assertTrue(scp.status == Document.STATUS_NEW)

        print("Authors seek review again.")
        scp.seek_review()
        print("Reviewer seeks approval.")
        scp.seek_approval()
        self.assertTrue(scp.status == Document.STATUS_INAPPROVAL)
        self.assertTrue(scp.can_approve())

        print("Approvers approve the ConceptPlan "
              "({2}) on Project {0} ({1}).".format(
                  p.__str__(), p.status, scp.status))
        scp.approve()
        print("Approvers have approved the ConceptPlan"
              " ({2}) on Project {0} ({1}).".format(
                  p.__str__(), p.status, scp.status))
        self.assertEqual(scp.status, Document.STATUS_APPROVED)

        print("Approving the ConceptPlan endorses the Project.")
        self.assertEqual(scp.project.status, Project.STATUS_PENDING)

        print("Endorsing the Project creates a ProjectPlan (SPP).")
        self.assertEqual(p.documents.instance_of(ProjectPlan).count(), 1)

        spp = p.documents.instance_of(ProjectPlan).get()
        self.assertEqual(spp.status, Document.STATUS_NEW)

        print("SPP can not be approved with empty mandatory fields.")
        self.assertFalse(p.can_approve())

        print("SPP needs Biometrician's endorsement.")
        

        print("SPP needs Program Leader's endorsement.")
        print("SPP needs Animal Ethics's endorsement if animals are involved.")
        print("SPP needs Herbarium Curator's endorsement"
              " only if plants are involved.")
        self.assertFalse(spp.involves_plants)
        self.assertTrue(spp.cleared_hc)

        print("SPP involves plants, HC endorsement required")
        spp.involves_plants = True
        spp.save()
        self.assertTrue(spp.involves_plants)
        self.assertFalse(spp.cleared_hc)
        self.assertTrue(spp.hc_endorsement, Document.ENDORSEMENT_REQUIRED)

        print("HC endorses SPP")
        spp.hc_endorsement = Document.ENDORSEMENT_GRANTED
        spp.save()
        self.assertTrue(spp.hc_endorsement, Document.ENDORSEMENT_GRANTED)
        self.assertTrue(spp.cleared_hc)


        # Test can_approve
        # self.assertTrue(p.can_approve())

    def test_reset_conceptplan_on_pending_scienceproject(self):
        """Resetting an approved SCP resets SCP and project to NEW."""
        print("Fast-forward SP to pending.")
        p = self.project
        scp = p.documents.instance_of(ConceptPlan).get()
        scp.seek_review()
        scp.seek_approval()
        scp.approve()
        self.assertEqual(scp.status, Document.STATUS_APPROVED)
        scp.reset()
        print("After reset, both ConceptPlan and Project must be STATUS_NEW")
        self.assertEqual(scp.status, Document.STATUS_NEW)
        self.assertEqual(p.status, Project.STATUS_NEW)
        print("Project setup should never spawn a second ConceptPlan")
        self.assertEqual(p.documents.instance_of(ConceptPlan).count(), 1)


    def test_active_project_transitions(self):
        """Test expected transitions for active ScienceProjects."""
        p = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
        self.assertTrue(p.can_request_update())
        self.assertTrue(p.can_suspend())
        self.assertTrue(p.can_terminate())

    # def test_request_update(self):
    #     """
    #     New ARARReports request an update from all active and closing projects.
    #     """
    #     p = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
    #     from datetime import datetime
    #     n = datetime.now()
    #     r = ARARReport.objects.create(year=p.year, date_open=n, date_closed=n)
    #     pr = p.documents.instance_of(ProgressReport)
    #     self.assertEqual(pr.count(), 1)
    #     self.assertEqual(pr.latest().status, Document.STATUS_NEW)
    #
    #     p.request_update()  # this should have happened during ARAR create
    #     self.assertEqual(p.status, Project.STATUS_UPDATE)

    # def test_complete_update(self):
    #     """
    #     ScienceProjects require an approved ProgressReport to complete the
    #     update.
    #     """
    #     self.project.status = Project.STATUS_UPDATE
    #     self.project.save()
    #     ProgressReport.objects.create(project=self.project,
    #                                   status=ProgressReport.STATUS_APPROVED)
    #     self.assertTrue(self.project.can_complete_update())
    #     self.project.complete_update()
    #     self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
    #
    # def test_request_closure(self):
    #     """Test requesting closure for active ScienceProject.
    #     """
    #     project = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
    #     self.assertTrue(project.can_request_closure())
    #     project.request_closure()
    #     self.assertTrue(project.status, Project.STATUS_CLOSURE_REQUESTED)
    #
    #     # TODO tests for other transitions


class CoreFunctionProjectModelTests(TestCase):
    """Test CoreFunction model methods, transitions, gate checks"""

    def new_CF_is_active(self):
        """A new CoreFunction has STATUS_ACTIVE immediately."""
        u = UserFactory.create()
        p = CoreFunctionProjectFactory.create(creator=u, project_owner=u)
        self.assertEqual(p.status, Project.STATUS_ACTIVE)

    def new_CF_has_conceptplan(self):
        """A new CoreFunction has one doc, a ConceptPlan."""
        u = UserFactory.create()
        p = CoreFunctionProjectFactory.create(creator=u, project_owner=u)
        self.assertEqual(p.documents.count(), 1)
        self.assertEqual(p.documents.instace_of(ConceptPlan).count(), 1)

    def test_that_active_CF_cannot_be_closed_without_closureform(self):
        """A CoreFunction requires an approved ClosureForm for closure."""
        u = UserFactory.create()
        p = CoreFunctionProjectFactory.create(creator=u, project_owner=u)
        p.status = Project.STATUS_ACTIVE
        p.save()
        self.assertFalse(p.can_complete())


class CollaborationProjectModelTests(TestCase):
    """CollaborationProject tests."""

    def test_new_collaboration_project(self):
        """A new CollaborationProject is ACTIVE.

        It does not require an approval process.
        """
        project = CollaborationProjectFactory.create()
        self.assertEqual(project.status, Project.STATUS_ACTIVE)

    def test_cannot_update(self):
        """Should be be able to request a general update of the Project details
        even if there's no progress report, or should be (currently) trust info
        to be up to date without separate prompt to update?
        """
        # project = CollaborationProjectFactory.create()
        # self.assertFalse(project.can_request_update())
        pass


class StudentProjectModelTests(TestCase):
    """StudentProject tests."""

    def test_new_student_project(self):
        """A new STP has no approval process and is ACTIVE."""
        project = StudentProjectFactory.create()
        self.assertEqual(project.status, Project.STATUS_ACTIVE)

    # def test_request_update_creates_student_report(self):
    #    project = StudentProjectFactory.create()
    #    project.request_update()
    #    self.assertEqual(StudentReport.objects.count(), 1)

    def test_studentproject_can_complete_update(self):
        """Completing the STP update requires an approved StudentReport."""
        project = StudentProjectFactory.create(status=Project.STATUS_UPDATE)
        self.assertFalse(project.can_complete_update())
        StudentReport.objects.create(project=project,
                                     status=StudentReport.STATUS_APPROVED)
        self.assertTrue(project.can_complete_update())
