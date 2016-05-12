from django.core.urlresolvers import reverse
from guardian.models import Group

from pythia.models import Program
from pythia.documents.models import ConceptPlan
from pythia.projects.models import ProjectMembership

from .base import BaseTestCase, UserFactory, ScienceProjectFactory


class ConceptPlanAdminTests(BaseTestCase):
    """ConceptPlan view tests.

    TODO: create users of all roles, test against all audiences.
    """

    def setUp(self):
        self.smt, created = Group.objects.get_or_create(name='SMT')
        self.scd, created = Group.objects.get_or_create(name='SCD')
        self.users, created = Group.objects.get_or_create(name='Users')

        self.user = UserFactory.create(username='test')
        self.user.is_superuser = True
        self.user.save()
        # self.user.groups.add(self.smt)
        # self.user.groups.add(self.scd)

        self.bob = UserFactory.create(
            username='bob', first_name='Bob', last_name='Bobson')
        self.john = UserFactory.create(
            username='john', first_name='John', last_name='Johnson')
        self.steven = UserFactory.create(
            username='steven', first_name='Steven', last_name='Stevenson')
        self.steven.groups.add(self.smt)
        self.fran = UserFactory.create(
            username='fran', first_name='Fran', last_name='Franson')
        self.fran.groups.add(self.smt)
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

        self.program = Program.objects.create(
                name="ConservationProgram",
                slug="conservationprogram",
                position=0,
                program_leader=self.fran)

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
        ProjectMembership.objects.create(
            project=self.project,
            user=self.john,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        self.project.save()
        self.client.login(username='bob', password='password')
        self.scp = self.project.documents.instance_of(ConceptPlan).get()
        self.url = reverse('admin:documents_conceptplan_change',
                           args=(self.scp.id,))
        self.tx_url = 'admin:documents_conceptplan_transition?transition={0}'

    def everyone_can_view_conceptplan(self):
        """Test that everyone can view the ConceptPlan"""
        # get ConceptPlan detail
        #     response = self.client.get(self.url)
        #     self.assertEqual(response.context['original'], self.plan)
        pass

    def only_team_can_change_conceptplan(self):
        """Test that only team can change ConceptPlan."""
        pass
        # conceptplan is not readonly to bob and john
        # conceptplan is readonly to peter

        # team changes conceptplan
        # data = {
        #     'id': self.scp.id,
        #     'summary': "New summary",
        #     'budget': '[["test"]]',
        #     'staff': '[["test"]]'
        #     }
        # response = self.client.post(self.url, data, follow=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(self.scp.summary, "New summary")

    def only_team_can_submit_conceptplan(self):
        """Test that only team can submit their ConceptPlan."""
        pass
        # bob and john can "seek_review" on ConceptPlan(new)
        # peter cannot "seek_review" on ConceptPlan(new)
        # should steven be able to "seek_review"?
        # bob and john can "recall", peter can't "recall" on CP(inreview)

    def only_reviewers_can_review_conceptplan(self):
        """Test that only reviewers can review a ConceptPlan.

        Reviewers include the project's PL as well as other SMT members.
        Only the project's PL sees the ConceptPlan in "My Tasks".
        """
        pass
        # bob, john, peter cannot "seek_approval" on ConceptPlan(inreview)
        # steven can "seek_approval" and "request_revision_from_authors"
        # fran can "seek_approval" and "request_revision_from_authors"
        # ConceptPlan is on steven's "My Tasks"
        # ConceptPlan is not in fran's "My Tasks"

    def only_approvers_can_approve_conceptplan(self):
        """Test that only approvers can approve a ConceptPlan."""
        pass
        # ConceptPlan(inapproval)
        # marge can "approve", "request_reviewer_revision", "request_author_revision".
        # steven, bob, peter can't "approve", "request_reviewer_revision", "request_author_revision".

    def submitted_conceptplan_is_readonly_to_team(self):
        """Test that a ConceptPlan(inreview) is readonly to team,
        but editable to reviewers and approvers."""
        # ConceptPlan(inreview)
        # readonly to peter, bob, john
        # editable to steven, fran, marge, user

    def test_concept_plan_read_only_superuser(self):
        """
        After approval the concept plan must still be editable to a super-user.
        """
        pass
    #     self.client.logout()
    #     self.client.login(username='user', password='password')
    #     self.scp.status = self.scp.STATUS_APPROVED
    #     self.scp.save()
    #     data = {
    #         'id': self.scp.id,
    #         'summary': "New summary",
    #         # 'budget': '[["test"]]', # TODO html table
    #         # 'staff': '[["test"]]' # TODO html table
    #         }
    #     response = self.client.post(self.url, data, follow=True)
    #     # self.assertEqual(response.status_code, 200)
    #     self.assertEqual(self.scp.summary, "New summary")
    #     # TODO test whether conceptplan is editable
    #
    # def test_concept_plan_seek_review(self):
    #     """A project team member can submit the ConceptPlan to seek review."""
    #     url = reverse(self.tx_url.format("seek_review"), args=(self.plan.pk,))
    #     self.assertEqual(self.scp.status, self.scp.STATUS_NEW)
    #     response = self.client.post(url, follow=True)
    #     # self.assertEqual(response.status_code, 200)
    #     # self.assertEqual(self.scp.status, self.scp.STATUS_INREVIEW)
    #
    # def test_concept_plan_review(self):
    #     pass
    #
    # def test_concept_plan_review_no_permission(self):
    #     "A user who isn't part of the project can't submit for review."
    #     self.client.login(username='peter', password='password')
    #     url = reverse(self.tx_url.format("seek_review"), args=(self.plan.pk,))
    #     response = self.client.post(url, follow=True)
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(self.scp.status, self.scp.STATUS_NEW)
