from django.core.urlresolvers import reverse

from pythia.documents.models import ConceptPlan
from pythia.templatetags.approvals import get_transitions

from .base import BaseTestCase, UserFactory, ScienceProjectFactory


class ApprovalTagsTests(BaseTestCase):
    def test_submit_for_review_action_with_permission(self):
        pass

    def test_submit_for_review_action_without_permission(self):
        pass

    def test_review_action_with_permission(self):
        pass

    def test_review_action_without_permission(self):
        pass
