"""View tests."""
from django.core.urlresolvers import reverse
from django.test import Client
# from django.test.client import RequestFactory
from guardian.models import Group

from pythia.models import Program
from pythia.documents.models import ConceptPlan, ProjectPlan
from pythia.projects.models import ProjectMembership

from .base import (BaseTestCase, ScienceProjectFactory,
                   ServiceFactory, DivisionFactory, ProgramFactory,
                   CoreFunctionProjectFactory, CollaborationProjectFactory,
                   StudentProjectFactory, UserFactory, SuperUserFactory)


class SmokeTest(BaseTestCase):
    """Poke each view in the eye and see if it twitches."""

    def setUp(self):
        """Set up."""
        self.client = Client()
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
        self.service = ServiceFactory.create(
            name='Service 1', slug='SVC1', creator=self.superuser, director=self.marge)
        self.service_empty = ServiceFactory.create(
            name='Service 2', slug='SVC2', creator=self.superuser, director=None)
        self.division = DivisionFactory.create(
            name='Division 1', slug='DIV1', creator=self.superuser, director=self.marge)
        self.division_empty = ServiceFactory.create(
            name='Division 2', slug='DIV2', creator=self.superuser, director=None)
        
        # ProgramFactory already sets division
        self.program = ProgramFactory.create(
            name="ScienceProgram",
            slug="scienceprogram",
            position=0,
            program_leader=self.steven)

        # ProjectFactory already sets program and output_program
        self.science_project = ScienceProjectFactory.create(
            # data_custodian=self.bob, site_custodian=self.bob,
            creator=self.bob, 
            modifier=self.bob, 
            project_owner=self.bob)

    def assert_200(self, url):
        """GET a given URL and assert that the response has status 200 OK."""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_project_choice(self):
        """Render Project choice landing page. 
        """
        url = reverse('admin:project_choice')
        self.assert_200(url)

    def test_service_changelist(self):
        """Render Service change_list. 
        
        Change list must be robust against missing values.
        Here, one Service has no Director set.
        """
        url = reverse('admin:pythia_service_changelist')
        self.assert_200(url)

    def test_division_changelist(self):
        """Render Division change_list. 
        
        Change list must be robust against missing values.
        Here, one Division has no Director set.
        """
        url = reverse('admin:pythia_division_changelist')
        self.assert_200(url)        

    def test_project_create(self):
        """Test that Project create_view loads without any further GET request parameters."""
        url = reverse('admin:projects_project_add')
        self.assert_200(url)

    def test_project_create_corefunction(self):
        """Test that Project create_view creates a CF project with ?project_type=1."""
        url = "{0}?project_type=1".format(reverse('admin:projects_project_add'))
        self.assert_200(url)

        # res = self.client.get(url)
        # self.assertEqual(res.context['form'].initial['project_type'], 1)

    def test_project_changelist(self):
        """Render Project change_list."""
        url = reverse('admin:projects_project_changelist')
        self.assert_200(url)

    def test_scienceproject_changelist(self):
        """Render ScienceProject change_list."""
        url = reverse('admin:projects_scienceproject_changelist')
        self.assert_200(url)

    def test_scienceproject_changeview(self):
        """Render ScienceProject change_view."""
        project = ScienceProjectFactory.create(
            program=self.program,
            project_owner=self.bob)
        url = project.absolute_url
        self.assert_200(url)

    def test_cfproject_changelist(self):
        """Render CFProject change_list."""
        url = reverse('admin:projects_corefunctionproject_changelist')
        self.assert_200(url)

    def test_cfproject_changeview(self):
        """Render CFProject change_view."""
        project = CoreFunctionProjectFactory.create(
            program=self.program,
            project_owner=self.bob)
        url = project.absolute_url
        self.assert_200(url)

    def test_extproject_changelist(self):
        """Render EXT Project change_list."""
        url = reverse('admin:projects_collaborationproject_changelist')
        self.assert_200(url)

    def test_extproject_changeview(self):
        """Render EXT Project change_view."""
        project = CollaborationProjectFactory.create(
            program=self.program,
            project_owner=self.bob)
        url = project.absolute_url  # convenience helper on Project
        self.assert_200(url)

    def test_studentproject_changelist(self):
        """Render StudentProject change_list."""
        url = reverse('admin:projects_studentproject_changelist')
        self.assert_200(url)

    def test_studentproject_changeview(self):
        """Render StudentProject change_view."""
        scienceproject = StudentProjectFactory.create(
            program=self.program,
            project_owner=self.bob)
        url = scienceproject.absolute_url
        self.assert_200(url)

    def test_conceptplan_changelist(self):
        """Render ConceptPlan changelist."""
        url = reverse("admin:documents_conceptplan_changelist")
        self.assert_200(url)

    def test_conceptplan_changeview(self):
        """Render ConceptPlan changeview."""
        scienceproject = ScienceProjectFactory.create(
            program=self.program,
            project_owner=self.bob)
        scp = scienceproject.documents.instance_of(ConceptPlan).get()
        url = scp.get_absolute_url()
        self.assert_200(url)

    def test_api_projects(self):
        """Test API endpoints /api/projects/"""
        scienceproject = ScienceProjectFactory.create(
            program=self.program,
            project_owner=self.bob)
        url = "/api/projects/"
        self.assert_200(url)

# TEST: User adds external user, enter username, password
# next screen add first name, last name etc, username must be ro
# check superuser fields are ro
# Test user updates own profile, all but superuser fields are ro

# TEST: ProgramAdminTest(BaseTestCase) - only editable to SMT + SCD


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
        self.division = DivisionFactory.create()
        self.program = Program.objects.create(
            division=self.division,
            name="ScienceProgram",
            slug="scienceprogram",
            position=0,
            program_leader=self.steven)

        self.project = ScienceProjectFactory.create(
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

    def assert_200(self, url):
        """GET a given URL and assert that the response has status 200 OK."""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_everyone_can_view_conceptplan(self):
        """Test that everyone can view the ConceptPlan."""
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
        # marge can "approve", "request_reviewer_revision",
        # "request_author_revision".
        # steven, bob, peter can't "approve", "request_reviewer_revision",
        # "request_author_revision".

    def test_conceptplan_inreview_is_readonly_to_team(self):
        """Test that a ConceptPlan(inreview) is readonly to team.

        Editable to reviewers and approvers.
        """
        # ConceptPlan(inreview)
        # readonly to peter, bob, john
        # editable to steven, fran, marge, user

    def test_conceptplan_inapproval_is_readonly_to_reviewers(self):
        """Test that a ConceptPlan(inreview) is readonly to team and reviewers.

        Editable to approvers.
        """
        # ConceptPlan(inapproval)
        # readonly to peter, bob, john, steven, fran
        # editable to marge, user

    def test_conceptplan_approved_is_readonly_to_all_but_superuser(self):
        """Test that a ConceptPlan(inreview) is readonly to all but SU.

        RO to Team, reviewers, and approvers, but editable to superusers.
        """
        # ConceptPlan(approved)
        # readonly to peter, bob, john, steven, fran, marge
        # editable to user

    def test_concept_plan_read_only_superuser(self):
        """Test that an approved ConceptPlan is still be editable to SU."""
        pass


class ProjectPlanAdminTests(BaseTestCase):
    """ProjectPlan view tests."""

    def setUp(self):
        """Set up."""
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
            position=1,
            program_leader=self.fran)

        self.project = ScienceProjectFactory.create(
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

    def assert_200(self, url):
        """GET a given URL and assert that the response has status 200 OK."""
        self.client.login(username='bob', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def assert_302(self, url):
        """GET a given URL and assert that the response has status 302 (redirect to login)."""
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)        

    def test_everyone_can_view_projectplan(self):
        """Test that everyone can view the ProjectPlan."""
        pass

    def test_only_team_can_change_projectplan(self):
        """Test that only team can change ProjectPlan."""
        pass

    def test_projectplan_exports(self):
        """Test document export."""
        pass
        # info = self.spp._meta.app_label, self.spp._meta.model_name
        # pdf_url = reverse('admin:%s_%s_download_pdf' % info, args=(self.spp.id,))
        # tex_url = reverse('admin:%s_%s_download_tex' % info, args=(self.spp.id,))
        # html_url = reverse('admin:%s_%s_download_html' % info, args=(self.spp.id,))
        
        # # response = self.client.get(url)
        # # self.assertEqual(response.status_code, 200)
        # self.assert_200(pdf_url)
        # # self.assert_200(tex_url)
        # # self.assert_200(html_url)