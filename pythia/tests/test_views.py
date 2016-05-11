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
        self.user.groups.add(self.smt)
        self.user.groups.add(self.scd)

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
        ProjectMembership.objects.create(
            project=self.project,
            user=self.john,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        self.project.save()
        self.client.login(username='bob', password='password')
        self.plan = self.project.documents.instance_of(ConceptPlan).get()
        self.url = reverse('admin:documents_conceptplan_change',
                           args=(self.plan.id,))

    # def test_get_concept_plan(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.context['original'], self.plan)

    def test_update_concept_plan(self):
        data = {
            'id': self.plan.id,
            'summary': "New summary",
            'budget': '[["test"]]',
            'staff': '[["test"]]'
            }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        plan = self.project.documents.instance_of(ConceptPlan).get()
        self.assertEqual(plan.summary, "New summary")

    def test_concept_plan_read_only_user(self):
        """
        An approved ConceptPlan is read-only to all but superusers.
        """
        self.plan.status = self.plan.STATUS_APPROVED
        self.plan.save()
        # original_summary = self.plan.summary
        data = {
            'id': self.plan.id,
            'summary': "New summary",
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        plan = self.project.documents.instance_of(ConceptPlan).get()
        #self.assertEqual(plan.summary, original_summary) # TODO: it's not set

    def test_concept_plan_read_only_superuser(self):
        """
        After approval the concept plan must still be editable to a super-user.
        """
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username='admin', password='password')
        self.plan.status = self.plan.STATUS_APPROVED
        self.plan.save()
        data = {
            'id': self.plan.id,
            'summary': "New summary",
            #'budget': '[["test"]]', # TODO html table
            #'staff': '[["test"]]' # TODO html table
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        plan = self.project.documents.instance_of(ConceptPlan).get()
        self.assertEqual(plan.summary, "New summary")
        # TODO test whether conceptplan is editable

    def test_concept_plan_seek_review(self):
        """A project team member can submit the ConceptPlan to seek review."""
        plan = self.project.documents.instance_of(ConceptPlan).get()
        url = reverse('admin:documents_conceptplan_transition', args=(plan.pk,))
        url += '?transition=seek_review'
        self.assertEqual(plan.status, plan.STATUS_NEW)
        response = self.client.post(url, follow=True)
        print(response)
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(self.plan.status, self.plan.STATUS_INREVIEW)

    def test_concept_plan_review(self):
        pass

    def test_concept_plan_review_no_permission(self):
        "A user who isn't part of the project can't submit for review."
        UserFactory.create(username='test2')
        self.client.login(username='test2', password='password')
        plan = self.project.documents.instance_of(ConceptPlan).get()
        url = reverse('admin:documents_conceptplan_transition',
                      args=(plan.pk,))
        url += '?transition=seek_review'
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)
        plan = self.project.documents.instance_of(ConceptPlan).get()
        self.assertEqual(plan.status, plan.STATUS_NEW)
