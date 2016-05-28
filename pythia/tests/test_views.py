from django.core.urlresolvers import reverse
from django.test import Client
from guardian.models import Group

from pythia.models import Program
from pythia.documents.models import ConceptPlan, ProjectPlan
from pythia.projects.models import ProjectMembership

from .base import (BaseTestCase, ProjectFactory, ScienceProjectFactory,
                   CoreFunctionProjectFactory, CollaborationProjectFactory,
                   StudentProjectFactory, UserFactory, SuperUserFactory)


class ConceptPlanAdminTests(BaseTestCase):
    """ConceptPlan view tests."""

    def setUp(self):
        """Create initial objects for test."""
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

        self.client = Client()
        self.scp = self.project.documents.instance_of(ConceptPlan).get()
        self.url = reverse('admin:documents_conceptplan_change',
                           args=(self.scp.id,))
        self.tx_url = 'admin:documents_conceptplan_transition?transition={0}'

    def test_everyone_can_view_conceptplan(self):
        """Test that everyone can view the ConceptPlan"""
        # get ConceptPlan detail
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # import ipdb; ipdb.set_trace()
        # print(response.context)
        # self.assertEqual(response.context['original'], self.scp)
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
        pass

    def test_only_team_can_change_conceptplan(self):
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

    def test_change_conceptplan_sets_modifier(self):
        """Test that Audit fields are correctly set on change.

        An authenticated request should set the request.user as modifier,
        and the date as modified on.
        An unauthenticated request (such as model tests) should default to the
        superuser (pk=1) as modifier, but should still set the date.
        """
        pass

    def test_only_team_can_submit_conceptplan(self):
        """Test that only team can submit their ConceptPlan."""
        pass
        # bob and john can "seek_review" on ConceptPlan(new)
        # peter cannot "seek_review" on ConceptPlan(new)
        # should steven be able to "seek_review"?
        # bob and john can "recall", peter can't "recall" on CP(inreview)

    def test_only_reviewers_can_review_conceptplan(self):
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

    def test_only_approvers_can_approve_conceptplan(self):
        """Test that only approvers can approve a ConceptPlan."""
        pass
        # ConceptPlan(inapproval)
        # marge can "approve", "request_reviewer_revision", "request_author_revision".
        # steven, bob, peter can't "approve", "request_reviewer_revision", "request_author_revision".

    def test_conceptplan_inreview_is_readonly_to_team(self):
        """Test that a ConceptPlan(inreview) is readonly to team,
        but editable to reviewers and approvers."""
        # ConceptPlan(inreview)
        # readonly to peter, bob, john
        # editable to steven, fran, marge, user

    def test_conceptplan_inapproval_is_readonly_to_reviewers(self):
        """Test that a ConceptPlan(inreview) is readonly to team and reviewers,
        but editable to approvers."""
        # ConceptPlan(inapproval)
        # readonly to peter, bob, john, steven, fran
        # editable to marge, user

    def test_conceptplan_approved_is_readonly_to_all_but_superuser(self):
        """Test that a ConceptPlan(inreview) is readonly to team, reviewers,
        and approvers, but editable to superusers."""
        # ConceptPlan(approved)
        # readonly to peter, bob, john, steven, fran, marge
        # editable to user


    def test_concept_plan_read_only_superuser(self):
        """
        After approval the concept plan must still be editable to a super-user.
        """
        pass

class ProjectPlanAdminTests(BaseTestCase):
    """ProjectPlan view tests."""

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
        self.change_url = reverse('admin:documents_projectplan_change',
                                  args=(self.scp.id,))
        self.tx_url = 'admin:documents_projectplan_transition?transition={0}'

        self.scp.seek_review()
        self.scp.seek_approval()
        self.scp.approve()
        self.spp = self.project.documents.instance_of(ProjectPlan).get()

    def test_everyone_can_view_projectplan(self):
        """Test that everyone can view the ProjectPlan"""
        pass

    def test_only_team_can_change_projectplan(self):
        """Test that only team can change ProjectPlan."""
        pass
