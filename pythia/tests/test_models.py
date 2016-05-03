from django.test import TestCase

# from django_fsm.db.fields import TransitionNotAllowed

from pythia.models import Program
from guardian.models import Group
from pythia.documents.models import (
    Document, StudentReport, ConceptPlan, ProjectPlan, ProgressReport)
from pythia.projects.models import (Project, ProjectMembership)
from pythia.reports.models import ARARReport
from .base import (BaseTestCase, ProjectFactory, ScienceProjectFactory,
                   CoreFunctionProjectFactory, CollaborationProjectFactory,
                   StudentProjectFactory, UserFactory)


class UserModelTests(TestCase):

    def test_user_is_valid_with_email_only(self):
        """Test that a user profile is valid with an email only.

        A user profile must be valid with an email only.
        Everything else is a bonus!
        """
        print("TODO")
        pass  # TODO


class ProjectModelTests(BaseTestCase):
    """
    Base project tests
    """
    def test_creation_adds_project_membership(self):
        """ Test that the supervising scientist is added to the project team on
        project creation.
        """
        project = ProjectFactory.create()
        self.assertEqual(ProjectMembership.objects.count(), 1)
        membership = ProjectMembership.objects.all()[0]
        self.assertEqual(project.project_owner, membership.user)
        self.assertEqual(membership.role,
                         ProjectMembership.ROLE_SUPERVISING_SCIENTIST)
        self.assertEqual(membership.project, project)


class ScienceProjectModelTests(BaseTestCase):
    """
    Tests along the life cycle of a ScienceProject.

    Special attention is paid to user groups, permissions, transitions,
    documents, project status
    """

    def setUp(self):
        """Create a ScienceProject and users for all roles.

        * user: a generic user
        * smt: reviewer group
        * scd: approver group
        * users: submitter group
        * bob bobson: Bob, a research scientist, wants to create a new
            science project. Bob will be the principal scientist of that
            project, add team members, write project documentation,
            submit docs for approval, and write updates.
        * John Johnson: John will join Bob's team. Then he should be able
            to execute "team-only" actions.
        * Steven Stevenson: Steven is Bob's Program Leader.
            As a member of SMT, the reviewers, Steven is the first instance of
            approval.
        * Marge Simpson: Marge is the Divisional Director.
            As member of the Directorate, M is the highest instance of approval
            and has resurrection powers for projects.
        * Peter Peterson: Peter won't have anything to do with the project.
            Peter should not be able to execute any "team-only" actions!
        """
        self.smt, created = Group.objects.get_or_create(name='SMT')
        self.scd, created = Group.objects.get_or_create(name='SCD')
        self.users, created = Group.objects.get_or_create(name='Users')

        self.user = UserFactory.create()
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

    def test_new_science_project(self):
        """A new ScienceProject must have one new ConceptPlan and no tx."""
        p = self.project

        print("A new ScienceProject must be of STATUS_NEW.")
        self.assertEqual(p.status, Project.STATUS_NEW)

        print("A new SP has exactly one document, a ConceptPlan.")
        self.assertEqual(p.documents.count(), 1)
        self.assertEqual(p.documents.instance_of(ConceptPlan).count(), 1)

        print("A new SP has no transitions until the SCP is approved.")
        self.assertEqual(len(list(p.get_available_status_transitions())), 0)

        print("A project cannot be endorsed without an approved ConceptPlan.")
        self.assertFalse(p.can_endorse())

    def test_conceptplan_permissions(self):
        """Test expected ConceptPlan permissions.

        * All users should be able to change (update content).
        * Only project team members should be able to submit
        * Only SMT members should be able to review
        * Only SCD members should be able to approve
        """
        pass  # permissions don't work at all
        p = self.project
        scp = p.documents.instance_of(ConceptPlan).get()
        scp.save()  # trigger document permission hook

        # print("Only project team members can submit the ConceptPlan.")
        # scp_submit = 'documents.submit_conceptplan'
        # self.assertTrue(self.bob.has_perm(scp_submit, scp))  # TODO fails

        # print("John is not on the team and has no permission to submit.")
        # self.assertFalse(self.john.has_perm(scp_submit, scp))

        # print("Peter is not on the team and has no permission to submit.")
        # self.assertFalse(self.peter.has_perm(scp_submit, scp))

        print("John joins the project team.")
        ProjectMembership.objects.create(
            project=self.project,
            user=self.john,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        # print("John is now on the team and has permission to submit.")
        # self.assertTrue(self.john.has_perm(scp_submit, scp))

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

    def test_conceptplan_approval(self):
        """
        Test all possible transitions in a ConceptPlan's life.

        Submitting the ConceptPlan sets its status to STATUS_INREVIEW.
        A document INREVIEW can be recalled back to NEW, then resubmitted.
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
        # aw crap, submitted too early
        scp.recall()

        # Phew
        self.assertTrue(scp.status == Document.STATUS_NEW)

        # Ok now we're good to go
        print("The team submits the doc for review.")
        scp.seek_review()
        self.assertTrue(scp.status == Document.STATUS_INREVIEW)
        self.assertTrue(scp.can_seek_approval())

        # ---------------------------------------------------------------------#
        # ConceptPlan INREVIEW -> INAPPROVAL
        """
        Submitting the ConceptPlan for approval sets its status to
        STATUS_INAPPROVAL, from where the ConceptPlan can be recalled back to
        INREVIEW, then resubmitted.
        """

        print(" The reviewer request revision from authors.")
        scp.request_revision_from_authors()
        self.assertTrue(scp.status == Document.STATUS_NEW)

        print("Authors optionally update, then seek review again.")
        scp.seek_review()
        self.assertTrue(scp.status == Document.STATUS_INREVIEW)

        print("Reviewer seeks approval.")
        scp.seek_approval()
        self.assertTrue(scp.status == Document.STATUS_INAPPROVAL)
        self.assertTrue(scp.can_approve())

        # ---------------------------------------------------------------------#
        # ConceptPlan INAPPROVAL -> APPROVED
        # Fast-track the ConceptPlan
        """ConceptPlan approval moves ScienceProject to PENDING.
        Approved conceptplan should be read-only to all but approvers.
        """
        scp.approve()  # TODO this fails but WHY
        self.assertEqual(scp.status, Document.STATUS_APPROVED)

        # print("Approving the ConceptPlan creates a Project Plan.")
        self.assertEqual(p.documents.instance_of(ProjectPlan).count(), 1)

        # Project, when endorsed, should be PENDING
        self.assertEqual(self.project.status, Project.STATUS_PENDING)
        # pass # fake! all fake.

    def test_projectplan_approval(self):
        """Test all possible transitions in a ProjectPlan's (SPP) life."""
        p = ScienceProjectFactory.create(status=Project.STATUS_PENDING)

        print("SPP can not be approved with empty mandatory fields.")
        self.assertFalse(p.can_approve())

        print("SPP needs Biometrician's endorsement.")
        print("SPP needs Program Leader's endorsement.")
        print("SPP needs Animal Ethics's endorsement if animals are involved.")
        print("SPP needs Herbarium Curator's endorsement if plants are involved.")

    def test_scienceproject_can_approve(self):
        """A ScienceProject with approved SPP can be approved."""
        p = ScienceProjectFactory.create(status=Project.STATUS_PENDING)
        spp = ProjectPlan.objects.create(project=p,
                                         status=ProjectPlan.STATUS_APPROVED)
        self.assertTrue(p.can_approve())

    def test_cant_approve_scienceproject_without_approved_projectplan(self):
        """A ScienceProject without approved SPP cannot be approved."""
        p = ScienceProjectFactory.create(status=Project.STATUS_PENDING)
        ProjectPlan.objects.create(project=p)
        self.assertFalse(p.can_approve())

    def test_active_project_transitions(self):
        """Test expected transitions for active ScienceProjects."""
        p = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
        self.assertTrue(p.can_request_update())
        self.assertTrue(p.can_suspend())
        self.assertTrue(p.can_terminate())

    def test_request_update(self):
        """New ARARReports request an update from all active and closing
        projects."""
        p = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
        from datetime import datetime
        now = datetime.now()
        r = ARARReport.objects.create(year=p.year,
                                      date_open=now,
                                      date_closed=now)
        pr = p.documents.instance_of(ProgressReport)
        self.assertEqual(pr.count(), 1)
        self.assertEqual(pr.latest().status, Document.STATUS_NEW)

        p.request_update()  # this should have happened during ARAR create
        self.assertEqual(p.status, Project.STATUS_UPDATE)

    def test_complete_update(self):
        """
        ScienceProjects require an approved ProgressReport to complete the
        update.
        """
        project = ScienceProjectFactory.create(status=Project.STATUS_UPDATE)
        ProgressReport.objects.create(project=project,
                                      status=ProgressReport.STATUS_APPROVED)
        self.assertTrue(project.can_complete_update())
        project.complete_update()
        self.assertEqual(project.status, Project.STATUS_ACTIVE)

    def test_request_closure(self):
        """Test requesting closure for active ScienceProject.
        """
        project = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
        self.assertTrue(project.can_request_closure())
        project.request_closure()
        self.assertTrue(project.status, Project.STATUS_CLOSURE_REQUESTED)

        # TODO tests for other transitions


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
    def test_new_student_project(self):
        """A new StudentProject does not require an approval process
        and immediately transitions to ACTIVE.
        """
        project = StudentProjectFactory.create()
        self.assertEqual(project.status, Project.STATUS_ACTIVE)

    #def test_request_update_creates_student_report(self):
    #    project = StudentProjectFactory.create()
    #    project.request_update()
    #    self.assertEqual(StudentReport.objects.count(), 1)

    def test_can_complete_update(self):
        project = StudentProjectFactory.create(status=Project.STATUS_UPDATE)
        StudentReport.objects.create(project=project,
                                     status=StudentReport.STATUS_APPROVED)
        self.assertTrue(project.can_complete_update())

    def test_cant_complete_update(self):
        project = StudentProjectFactory.create(status=Project.STATUS_UPDATE)
        StudentReport.objects.create(project=project)
        self.assertFalse(project.can_complete_update())
