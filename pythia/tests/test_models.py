from django.test import TestCase

from django_fsm.db.fields import TransitionNotAllowed

from pythia.models import Program
from guardian.models import Group
from pythia.documents.models import (
    Document, StudentReport, ConceptPlan, ProjectPlan, ProgressReport)
from pythia.projects.models import (
    Project, ScienceProject, CoreFunctionProject, CollaborationProject,
    StudentProject, ProjectMembership)

from .base import (BaseTestCase,
        ProjectFactory, ScienceProjectFactory,
        CoreFunctionProjectFactory, CollaborationProjectFactory,
        StudentProjectFactory, UserFactory)


class UserModelTests(TestCase):

    def test_user_is_valid_with_email_only(self):
        """Email is the unique user id.

        A user profile must be valid with an email only.
        Everything else is a bonus!
        """
        print("TODO")
        pass # TODO


class ProjectModelTests(BaseTestCase):
    """
    Base project tests
    """
    def test_creation_adds_project_membership(self):
        """The user nominated as supervising scientist must be also added to the
        team list on Project creation.
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
        # a generic user
        self.user = UserFactory.create()

        # Two user groups, SMT (Sci Mgmt Team) and SCDD (SCD Directorate)
        self.smt, created = Group.objects.get_or_create(name='SMT')
        self.scd, created = Group.objects.get_or_create(name='SCD')
        self.users, created = Group.objects.get_or_create(name='Users')

        # Bob, a research scientist, wants to create a new science project.
        # Bob will be the principal scientist of that project, add team members,
        # write project documentation, submit docs for approval, and write updates.
        self.bob = UserFactory.create(
                username='bob',
                first_name='Bob',
                last_name='Bobson')

        # John will join Bob's team. Then he should be able to execute
        # "team-only" actions.
        self.john = UserFactory.create(
                username='john',
                first_name='John',
                last_name='Johnson')

        # Steven is Bob's Program Leader.
        # As a member of SMT, Steven is the first instance of approval.
        self.steven = UserFactory.create(
                username='steven',
                first_name='Steven',
                last_name='Stevenson')
        #self.steven.groups.add(Group.objects.get(name='SMT'))
        self.steven.groups.add(self.smt)

        # Marge is the Divisional Director.
        # As member of the Directorate, M is the highest instance of approval and has
        # resurrection powers for projects.
        self.marge = UserFactory.create(
                username='marge',
                first_name='Marge',
                last_name='Simpson')
        self.marge.groups.add(self.scd)

        # Peter won't have anything to do with the project.
        # Peter should not be able to execute any "team-only" actions!
        self.peter = UserFactory.create(
                username='peter',
                first_name='Peter',
                last_name='Peterson')

        self.program = Program.objects.create(
                name="ScienceProgram",
                slug="scienceprogram",
                position=0,
                program_leader=self.steven)

        self.project = ScienceProjectFactory.create(
            creator=self.bob,
            modifier=self.bob,
            program=self.program,
            #data_custodian=self.bob, site_custodian=self.bob, # not nominated yet
            project_owner=self.bob)


    def test_project_life_cycle(self):
        """Test all steps in a ScienceProject's life.

        Emphasis on transitions, pre- and postconditions, gate checks.

        """
        #---------------------------------------------------------------------#
        # New project
        print("A new ScienceProject must be of STATUS_NEW.")
        self.assertEqual(self.project.status, Project.STATUS_NEW)

        print("A new SP has exactly one ConceptPlan")
        self.assertEqual(ConceptPlan.objects.count(), 1)

        print("A new SP has no transitions until the SCP is approved.")
        self.assertEqual(self.project.get_available_status_transitions(), [])

        print("The gate check can_endorse() tests for an approved ConceptPlan.")
        self.assertFalse(self.project.can_endorse())

        # Bob is project owner, John joins the team, Peter won't join
        scp = self.project.documents.instance_of(ConceptPlan).get()

        #---------------------------------------------------------------------#
        # Member permissions
        print("Only project team members can submit the ConceptPlan.")
        # Bob's your uncle (and project owner)
        self.assertTrue(self.bob.has_perm('submit_conceptplan', scp))

        print("Non-team members don't have permission to submit the ConceptPlan.")
        # John's not on the team yet
        self.assertFalse(self.john.has_perm('submit_conceptplan', scp))
        # And Peter will never be (nothing personal though)
        self.assertFalse(self.peter.has_perm('submit_conceptplan', scp))

        # John joins the team
        pm = ProjectMembership.objects.create(
                project=self.project,
                user=self.john,
                role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        # Now John can submit the ConceptPlan
        self.assertTrue(self.john.has_perm('submit_conceptplan', scp))

        print("Only Program Leaders (reviewers) can review.")
        # TODO find the correct permission
        # The Program Leader has permission "review", not Team
        #self.assertTrue(self.steven.has_perm('review_conceptplan', scp))
        self.assertFalse(self.bob.has_perm('review_conceptplan', scp))

        print("Only Directorate (approvers) can approve.")
        # The Directorate has permission "approve", not PL, not Team
        # TODO find the correct permission
        #self.assertTrue(self.marge.has_perm('approve_conceptplan', scp))
        self.assertFalse(self.steven.has_perm('approve_conceptplan', scp))
        self.assertFalse(self.bob.has_perm('approve_conceptplan', scp))

        # Update the Project:  only project members and higher can update (currently everyone can)
        # TODO find permission name
        #self.assertTrue(self.steven.has_perm('projects.change_scienceproject', self.project))
        #self.assertTrue(self.bob.has_perm('projects.change_scienceproject', self.project))
        #self.assertTrue(self.john.has_perm('project.change_scenceproject', self.project))


        # TODO Update the ConceptPlan:  only project members and higher can update (currently everyone can)
        self.assertTrue(self.steven.has_perm('pythia.change_conceptplan', scp))
        self.assertTrue(self.bob.has_perm('pythia.change_conceptplan', scp))
        self.assertTrue(self.john.has_perm('pythia.change_conceptplan', scp))
        # Peter is not on the team and shouldn't be able to change
        self.assertFalse(self.peter.has_perm('pythia.change_conceptplan', scp))

        #---------------------------------------------------------------------#
        # ConceptPlan NEW -> INREVIEW
        """Submitting the ConceptPlan sets its status to STATUS_INREVIEW.
        A document INREVIEW can be recalled back to NEW, then resubmitted.
        """
        print("The ConceptPlan is new and ready to be submitted (no need to fill in fields)")
        self.assertTrue(scp.status == Document.STATUS_NEW)
        self.assertTrue(scp.can_seek_review())

        print("The team submits for review")
        scp.seek_review()
        # The SCP sits with the Program Leader now
        self.assertTrue(scp.status == Document.STATUS_INREVIEW)
        self.assertTrue(scp.can_seek_approval())

        print("The team recalls the document from review")
        # aw crap, submitted too early
        scp.recall()

        # Phew
        self.assertTrue(scp.status == Document.STATUS_NEW)

        # Ok now we're good to go
        print("The team submits the doc for review")
        scp.seek_review()
        self.assertTrue(scp.status == Document.STATUS_INREVIEW)
        self.assertTrue(scp.can_seek_approval())

        #---------------------------------------------------------------------#
        # ConceptPlan INREVIEW -> INAPPROVAL
        """Submitting the ConceptPlan for approval sets its status to STATUS_INAPPROVAL.
        A document INAPPROVAL can be recalled back to INREVIEW, then resubmitted.
        """

        print(" The reviewer sends the doc back: Request revision from authors")
        scp.request_revision_from_authors()
        self.assertTrue(scp.status == Document.STATUS_NEW)

        print("Authors optionally update, then seek review again")
        scp.seek_review()
        self.assertTrue(scp.status == Document.STATUS_INREVIEW)

        print("Reviewer sends doc forward: Reviewer seeks approval")
        scp.seek_approval()
        self.assertTrue(scp.status == Document.STATUS_INAPPROVAL)
        self.assertTrue(scp.can_approve())

        #---------------------------------------------------------------------#
        # ConceptPlan INAPPROVAL -> APPROVED
        # Fast-track the ConceptPlan
        """ConceptPlan approval moves ScienceProject to PENDING.
        Approved conceptplan should be read-only to all but approvers.
        """
        scp.approve()
        print("Approving the ConceptPlan creates a Project Plan, SPP")
        self.assertEqual(ProjectPlan.objects.count(), 1)
        self.assertEqual(scp.status, Document.STATUS_APPROVED)

        # Project, when endorsed, should be PENDING
        self.assertEqual(self.project.status, Project.STATUS_PENDING)


    def test_projectplan_transitions(self):
        """Test ProjectPlan transitions from within project life cycle.
        """
        self.assertEqual(ConceptPlan.objects.count(), 1)
        scp = self.project.documents.instance_of(ConceptPlan).get()
        scp.seek_review()
        scp.seek_approval()
        scp.approve()
        # triggers self.project.endorse()
        self.assertEqual(scp.status, Document.STATUS_APPROVED)
        self.assertEqual(self.project.status, Project.STATUS_PENDING)


        self.assertEqual(ProjectPlan.objects.count(), 1)
        spp = self.project.documents.instance_of(ProjectPlan).get()
        # require endorsements of pl, bm, hc, ae, (not dm yet)
        # test can seek review

        # test cannot seek approval without endorsements
        # add endorsements
        # test can seek approval
        # approve
        # project.approve
        # project status active
        pass

    def test_suspend_active_project(self):
        pass

    def test_terminate_active_project(self):
        pass

    def test_request_project_update(self):
        # request update
        # progressreport approval
        # approve update
        # test project status is active again
        pass

    def test_request_closure(self):
        # can submitters request closure?
        # projectclosure approval
        # project status pending_final_update
        pass

    def test_request_final_update(self):
        # progressreport approval
        # project status completed
        pass




    '''
    def test_move_to_pending_approval_not_allowed(self):
        project = ScienceProjectFactory.create()
        self.assertRaises(TransitionNotAllowed, project.approve())

    def test_scienceproject_can_approve(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_PENDING)
        ProjectPlan.objects.create(project=project, status=ProjectPlan.STATUS_APPROVED)
        self.assertTrue(project.can_approve())

    def test_cant_approve(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_PENDING)
        ProjectPlan.objects.create(project=project)
        self.assertFalse(project.can_approve())

    def test_approval(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_PENDING)
        ProjectPlan.objects.create(project=project, status=ProjectPlan.STATUS_APPROVED)
        user = project.project_owner
        project.approve()
        self.assertTrue(project.status, project.STATUS_ACTIVE)
        #self.assertTrue(user.has_perm('close_scienceproject', project)) # TODO find permission name

    def test_approval_not_allowed(self):
        project = ScienceProjectFactory.create()
        self.assertRaises(TransitionNotAllowed, project.approve)

    def test_can_request_update(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
        self.assertTrue(project.can_request_update())

    def test_cant_request_update(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_NEW)
        #self.assertFalse(project.can_request_update())
        self.assertRaises(TransitionNotAllowed, project.request_update)

    def test_request_update(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
        self.assertEqual(ProgressReport.objects.count(), 0)
        project.request_update()
        self.assertEqual(ProgressReport.objects.count(), 1)
        self.assertEqual(project.status, Project.STATUS_UPDATE)

    def test_can_complete_update(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_UPDATE)
        ProgressReport.objects.create(project=project,
                                      status=ProgressReport.STATUS_APPROVED)
        self.assertTrue(project.can_complete_update())

    def test_complete_update(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_UPDATE)
        ProgressReport.objects.create(project=project,
                                      status=ProgressReport.STATUS_APPROVED)
        project.complete_update()
        self.assertEqual(project.status, Project.STATUS_ACTIVE)

    def test_can_request_closure(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
        self.assertTrue(project.can_request_closure())

    def test_request_closure(self):
        project = ScienceProjectFactory.create(status=Project.STATUS_ACTIVE)
        project.request_closure()
        self.assertTrue(project.status, Project.STATUS_CLOSURE_REQUESTED)
    '''
class CoreFunctionProjectModelTests(TestCase):
    #def test_new_core_function_project(self):
    #    project = CoreFunctionProjectFactory.create()
    #    self.assertEqual(project.status, Project.STATUS_ACTIVE)

    #def test_cannot_close(self):
    #    project = CoreFunctionProjectFactory.create()
    #    self.assertFalse(project.can_complete())

    pass

class CollaborationProjectModelTests(TestCase):
    def test_new_collaboration_project(self):
        """A new CollaborationProject does not require an approval process
        and immediately transitions to ACTIVE.
        """
        project = CollaborationProjectFactory.create()
        self.assertEqual(project.status, Project.STATUS_ACTIVE)

    def test_cannot_update(self):
        """Should be be able to request a general update of the Project details
        even if there's no progress report, or should be (currently) trust info
        to be up to date without separate prompt to update?
        """
        project = CollaborationProjectFactory.create()
        #self.assertFalse(project.can_request_update())
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


class ConceptPlanTests(TestCase):
    def test_new_concept_plan(self):
        project = ScienceProjectFactory.create()
        plan = project.documents.instance_of(ConceptPlan).get()
        self.assertEqual(ConceptPlan.objects.count(), 1)
        self.assertEqual(plan.status, ConceptPlan.STATUS_NEW)

    def test_concept_plan_project_members_can_submit(self):
        project = ScienceProjectFactory.create()
        plan = project.documents.instance_of(ConceptPlan).get()
        #user = UserFactory.create()
        #ProjectMembership.objects.create(
        #    project=project, user=user,
        #    role=ProjectMembership.ROLE_SUPERVISING_SCIENTIST
        #)

        # TODO: set permissions
        #for user in project.members.all():
        #    #self.assertTrue(user.has_perm("submit_conceptplan", plan))
        #    self.assertTrue(user.has_perm("submit", plan))

    def test_can_seek_review(self):
        """
        Test that a concept plan can have endorsements added.
        """
        project = ScienceProjectFactory.create()
        plan = project.documents.instance_of(ConceptPlan).get()
        self.assertTrue(plan.can_seek_review())

    def test_submit_for_review(self):
        project = ScienceProjectFactory.create()
        plan = project.documents.instance_of(ConceptPlan).get()
        plan.seek_review()
        self.assertEqual(plan.status, plan.STATUS_INREVIEW)

    def test_can_seek_approval(self):
        """
        Test that a concept plan can seek approval.
        """
        project = ScienceProjectFactory.create()
        plan = project.documents.instance_of(ConceptPlan).get()
        self.assertTrue(plan.can_seek_approval())

    def test_submit_for_approval(self):
        project = ScienceProjectFactory.create()
        plan = project.documents.instance_of(ConceptPlan).get()
        plan.status = plan.STATUS_INREVIEW
        plan.save()
        plan.seek_approval()
        self.assertEqual(plan.status, plan.STATUS_INAPPROVAL)

    def test_not_ready_for_approval(self):
        """
        Test that a new concept plan can't be approved.
        """
        project = ScienceProjectFactory.create()
        plan = project.documents.instance_of(ConceptPlan).get()
        self.assertRaises(TransitionNotAllowed, plan.approve)

    def test_can_approve(self):
        project = ScienceProjectFactory.create()
        plan = project.documents.instance_of(ConceptPlan).get()
        plan.status = plan.STATUS_INAPPROVAL
        plan.save()
        self.assertTrue(plan.can_approve())

    def test_approval(self):
        project = ScienceProjectFactory.create()
        plan = project.documents.instance_of(ConceptPlan).get()

        # fast forward to approval:
        plan.seek_review()
        plan.seek_approval()
        plan.approve()

        #project = ScienceProject.objects.get(pk=project.pk)
        self.assertEqual(plan.status, plan.STATUS_APPROVED)
        self.assertEqual(project.status, project.STATUS_PENDING)

    def test_can_update(self):
        pass


class ProjectPlanTests(TestCase):
    """
    Check everything needed to approve the project plan
    """

class ProgressReportTest(TestCase):
    pass


class ProjectClosureTest(TestCase):
    pass


class StudentReportTest(TestCase):
    pass
