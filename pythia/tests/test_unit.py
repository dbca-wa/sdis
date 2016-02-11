from django.contrib.auth.models import Group
from django.test import TestCase
from django.test.client import RequestFactory

from pythia.templatetags.approvals import get_transitions
from pythia.documents.models import ConceptPlan
from pythia.projects.models import (
    Project, ScienceProject, CoreFunctionProject, CollaborationProject,
    StudentProject, ProjectMembership)

from .base import (BaseTestCase, ProjectFactory, ScienceProjectFactory,
                   CoreFunctionProjectFactory, CollaborationProjectFactory,
                   StudentProjectFactory, UserFactory)

class TemplateTagTests(BaseTestCase):
    def setUp(self):
        users, created = Group.objects.get_or_create(name='Users')
        self.project = ScienceProjectFactory.create()
        self.user = UserFactory.create(is_superuser=True)

    def test_get_transitions_approved(self):
        """
        Test that get_transitions has transitions in approved state.
        """
        request = RequestFactory()
        request.user = self.user

        context = {'request': request}

        plan = self.project.documents.instance_of(ConceptPlan).get()
        plan.status = 'approved'
        plan.save()

        output = get_transitions(context, plan)
        print output
        #self.fail("blah")
        pass

class AreaTest(BaseTestCase):
    def dummy_fail():
        self.fail("blah")

class RegionTest(BaseTestCase):
    pass

class DistrictTest(BaseTestCase):
    pass

class AddressTest(BaseTestCase):
    pass

class DivisionTest(BaseTestCase):
    pass
