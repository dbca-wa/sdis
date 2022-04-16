from __future__ import unicode_literals

from django.conf import settings
from django.contrib.admin.tests import AdminSeleniumWebDriverTestCase
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
# from django.contrib.auth.models import Group
from guardian.models import Group
from django.contrib.sessions.backends.db import SessionStore
from django.core.urlresolvers import reverse
from django.utils.module_loading import import_by_path
from django.test.utils import override_settings

from unittest import SkipTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from pythia.projects.models import *
from pythia.documents.models import *
from pythia.tests.base import (
    SuperUserFactory, UserFactory, ScienceProjectFactory)

import pdb

TEST_EMAIL = "florian.wendelin.mayer@gmail.com"


@override_settings(
    AUTHENTICATION_BACKENDS=('django.contrib.auth.backends.ModelBackend'),)
class BaseLiveServerTestCase(AdminSeleniumWebDriverTestCase):
    """
    Base selenium test case. Override any custom user settings, to make the
    testing simpler. Ensure if you are testing these features to re-add them
    on the test case in question.
    """
    # Set this to None to prevent AdminSeleniumWebDriverTestCase from limiting
    # our installed apps.
    available_apps = None

    def create_preauthenticated_session(self, user):
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()

        # to set a cookie we need to first visit the domain.
        self.selenium.get(self.live_server_url)
        self.selenium.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/',
            ))

    def switch_to_window(self, partial_title):
        """
        Switch to the window that contains the title ``partial_title``, fail
        if a window containing ``partial_title`` could not be found.
        """
        def window_found(driver):
            for handle in driver.window_handles:
                self.selenium.switch_to_window(handle)
                if partial_title in self.selenium.title:
                    return True

        self.wait_until(window_found)

    # This is added in Django 1.7, we can remove it once we upgrade.
    def wait_for(self, css_selector, timeout=10):
        """
        Helper function that blocks until an css selector is found on the page.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as ec
        self.wait_until(
            ec.presence_of_element_located((By.CSS_SELECTOR, css_selector)),
            timeout)


    # This is added in Django 1.7, we can remove it once we upgrade.
    def wait_for_text(self, css_selector, text, timeout=10):
        """
        Helper function that blocks until the text is found in the css
        selector.
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as ec
        self.wait_until(
            ec.text_to_be_present_in_element(
                (By.CSS_SELECTOR, css_selector), text),
            timeout)


class LoginTests(BaseLiveServerTestCase):
    """
    Functional testing of the login and user registration workflow.
    """
    def setUp(self):
        """Create a User using the UserFactory.
        """
        self.user = UserFactory.create()

    def test_login(self):
        """Test whether the admin can login.
        """
        self.admin_login(self.user.username, 'password')

        # He checks to see if there the homepage is displayed properly and
        # he is logged in.
        header_text = self.selenium.find_element_by_tag_name('h1').text
        welcome_text = self.selenium.find_element_by_xpath(
            '//div[@class="jumbotron"]/p').text
        self.assertIn('Science Directorate Information System', header_text)
        self.assertIn(self.user.first_name, welcome_text)


class ProfileTests(BaseLiveServerTestCase):
    """
    Functional testing of user profile management. Currently empty.
    """

    def setUp(self):
        """Create a User using the UserFactory."""
        self.user_a = UserFactory.create()
        self.user_b = UserFactory.create()
        self.superuser = SuperUserFactory.create()

    def test_user_can_update_own_profile(self):
        """A user should be able to update own details, but not set permissions.

        Fields that should be read-only to the user when viewing own profile:
        ('is_superuser', 'is_active', 'is_staff', 'date_joined', 'groups')

        All other fields should be writeable.
        """
        # self.user_a.login()
        # view own profile
        # assert readonly fields are readonly
        pass

    def test_user_can_view_other_user_profiles(self):
        """To a non-superuser, other profiles should be read-only.
        The user should be able to see all fields.
        """
        pass

    def test_superuser_can_update_user_profile(self):
        """A superuser should be able to update all fields on a
        User profile.
        """
        pass


class ProjectTests(BaseLiveServerTestCase):
    def test_create_project_enduser(self):
        """
        Test whether a user can create a project.

        * Creates a standard user
        * User logs in
        * User goes to "add project" url
        * add project form opens
        * TODO what should be there
        * TODO user saves project
        * TODO what should be there

        """
        user = UserFactory.create(username='someone')
        self.create_preauthenticated_session(user)
        url = reverse('admin:projects_project_add')
        self.selenium.get("%s%s" % (self.live_server_url, url))
        self.wait_page_loaded()

        # Project year and number should be hidden and auto-set

        # TODO add stuff
        # self.fail("Finish this test")
        pass

    def test_create_project_superuser(self):
        """
        Test that a superuser can add a project.
        """
        # the normal user logs in
        admin = UserFactory.create(username='admin', is_superuser=True)
        self.create_preauthenticated_session(admin)

        # and clicks on "create a new project"
        url = reverse('admin:projects_project_add')
        self.selenium.get("%s%s" % (self.live_server_url, url))
        self.wait_page_loaded()

        # Project year should be shown and auto-set to current year

        # Project number should be shown and auto-set to next available
        # within current year

        # self.fail("Finish this test")
        pass


class ScienceProjectApprovalTests(BaseLiveServerTestCase):
    """
    Functional testing of project and document approvals.

    Full walkthrough of project and document life cycle.
    """
    def setUp(self):
        """Setup the ScienceProjectApprovalTest.

        Create groups and users.
        """
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
            username='bob', first_name='Bob', last_name='Bobson')

        # John will join Bob's team. Then he should be able to execute
        # "team-only" actions.
        self.john = UserFactory.create(
            username='john', first_name='John', last_name='Johnson')

        # Steven is Bob's Program Leader.
        # As a member of SMT, Steven is the first instance of approval.
        self.steven = UserFactory.create(
            username='steven', first_name='Steven', last_name='Stevenson')
        # self.steven.groups.add(Group.objects.get(name='SMT'))
        self.steven.groups.add(self.smt)

        # Marge is the Divisional Director.
        # As member of the Directorate, M is the highest instance of approval
        # and has resurrection powers for projects.
        self.marge = UserFactory.create(
            username='marge', first_name='Marge', last_name='Simpson')
        self.marge.groups.add(self.scd)

        # Peter won't have anything to do with the project.
        # Peter should not be able to execute any "team-only" actions!
        self.peter = UserFactory.create(
            username='peter', first_name='Peter', last_name='Peterson')

        self.project = ScienceProjectFactory.create(
            # data_custodian=self.bob, site_custodian=self.bob,
            creator=self.bob, 
            modifier=self.bob, 
            project_owner=self.bob)

    def test_new_project_status(self):
        """Test that the new project has the correct status.
        """
        self.assertEqual(self.project.status, Project.STATUS_NEW)

    def test_new_project_has_documents(self):
        """Test whether new project has correct documents.

        A new ScienceProject needs to have a new, empty ConceptPlan.
        Let's assume the ConceptPlan is empty if the first field, "summary",
        is empty.
        """
        self.assertEqual(
            self.project.documents.instance_of(ConceptPlan).count(), 1)
        conceptplan = self.project.documents.instance_of(ConceptPlan).get()
        self.assertEqual(conceptplan.status, Document.STATUS_NEW)
        # self.assertEqual(conceptplan.summary, "")

        # Bob logs in
        self.create_preauthenticated_session(self.bob)

        # Bob sees the project in the My Projects list
        # TODO

        # He browses to the project
        url = reverse('admin:projects_scienceproject_change',
                      args=(self.project.id,))
        self.selenium.get("%s%s" % (self.live_server_url, url))
        self.wait_page_loaded()

        # Breadcrumb must show "Home", "All Projects", project.type_year_number
        # TODO

        # Actions: "No actions available at this time"

        # There must be a ConceptPlan tab with label "Concept Plan"
        heading = self.selenium.find_element_by_xpath(
            '//*[@id="wrap"]/div/div[2]/div/div/ul[2]/li[2]/a').text
        self.assertIn('Concept Plan', heading)

    def test_new_conceptplan_permissions_public(self):
        """Test permissions of non-team members to the new ConceptPlan.

        The ConceptPlan should be readable to non-team members.
        Criterion: no "save changes" button.
        """
        # Non team-member Peter logs in
        self.create_preauthenticated_session(self.peter)

        conceptplan = self.project.documents.instance_of(ConceptPlan).get()

        url = reverse('admin:documents_conceptplan_change', args=(conceptplan.id,))
        self.selenium.get("%s%s" % (self.live_server_url, url))
        self.wait_page_loaded()

    def test_new_conceptplan_permissions_team(self):
        """Test permissions of non-team members to the new ConceptPlan.
        """


        # Peter should see the ConceptPlan read-only
        # TODO

        # Peter should not see the "save changes" button

        # The SCP must be readable to all users

        # The SCP must be editable to team and higher (all but Peter)

        # The Project team and higher must be able to submit the SCP for
        # review to the PL



        # Bob clicks on the ConceptPlan
        # ConceptPlan must be new: Status New document
        # Actions: Submit for review
        pass


    def test_project_add_teammember(self):
        # TODO Bob adds John to the team
        ProjectMembership.objects.create(
            project=self.project,
            user=self.john,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)
        self.assertEqual(
                ProjectMembership.objects.filter(project=self.project).count(),
                2)

        # The new team member must have team permissions
        # TODO

    def test_projectmembership_ordering_by_position_ascending(self):
        # change ordering: set bob's position lower than john's position
        # get project members, assert bob is listed first
        print('TODO: test whether project team is ordered by membership position!')
        pass

    def test_submitting_concept_plan_for_review(self):
        """The project owner submits a ConceptPlan for review."""
        # Bob has created a project, and now wants to complete the concept
        # plan so that he can get it approved.
        plan = self.project.documents.instance_of(ConceptPlan).get()

        # Let's pretend someone has already filled in the ConceptPlan
        plan.status = plan.STATUS_NEW
        plan.summary = "Project summary"
        plan.outcome = "Expected project outcome"
        plan.collaborations = "Project collaborations"
        plan.strategic = "Strategic context"
        plan.staff = [["insert"], ["here"]]
        plan.budget = [["expected"], ["budget"]]
        #plan.director_scd_comment = "Science director's comment"
        #plan.director_outputprogram_comment = "Output director's comment"
        plan.save()
        plan.setup() # this should call update_document_permissions()
        # which will assign guardian permissions

        # Bob logs in
        self.create_preauthenticated_session(self.bob)
        #pdb.set_trace()
        # He browses to the url of his concept plan.
        url = reverse('admin:documents_conceptplan_change', args=(plan.id,))
        self.selenium.get("%s%s" % (self.live_server_url, url))
        self.wait_page_loaded()

        # The project title in summary form is displayed in the
        # breadcrumbs and that the status is "New document".
        #bc = self.selenium.find_element_by_class_name("breadcrumb")
        #print('Breadcrumb: {0}'.format(bc))
        # TODO  'WebElement' is not iterable - get last element of WebElement bc
        #self.assertIn(self.project.project_type_year_number, bc)

        # TODO syntax error on assertEqual!?
        #self.assertEqual(
        #    self.selenium.find_element_by_id('document_status').text,
        #    plan.get_status_display()) # TODO not equal

        # A button is available to submit his plan to SMT for approval.
        #approval_button = self.selenium.find_element_by_id('id_inreview')
        #self.assertEqual(approval_button.text, 'Submit for review')

        # Bob clicks the button, which should take him to a confirmation page.
        #approval_button.click()
        #self.wait_page_loaded()

        # TODO Bob cancels and returns to the unsubmitted ConceptPlan.

        # On the confirmation page, Bob confirms his desire to submit
        # the concept plan for review.
        #self.selenium.find_element_by_id('id_confirm').click()
        #self.wait_page_loaded()

        # Bobs confirmation sends the system into a spin and it kicks the
        # concept plan into the state "Review requested". Success!
        #plan = self.project.documents.instance_of(ConceptPlan).get()
        #status = self.selenium.find_element_by_id('document_status').text
        #self.assertEqual(status, plan.get_status_display())
        pass

    def test_adding_endorsement_to_conceptplan_new(self):
        """Test adding an endorsement while the document is new.

        Endorsements do not cause actions like approvals or rejections.
        A team member can endorse a document to say she's got nothing more to add.
        John, who is on the project's team, adds an endorsement to the document.
        This serves to signal others that John endorses the document, and requires
        no further updates from his perspective.
        """
        pass
        # TODO

    def test_adding_endorsement_to_conceptplan_in_review(self):
        """Test adding an endorsement while the document is in review.

        Endorsements do not cause actions like approvals or rejections.
        Each SMT member can endorse a document to indicate his personal OK, whereas
        the decision will be made by the whole SMT.
        """

        plan = self.project.documents.instance_of(ConceptPlan).get()

        plan.status = plan.STATUS_INREVIEW
        plan.summary = "Project summary"
        plan.outcome = "Expected project outcome"
        plan.collaborations = "Project collaborations"
        plan.strategic = "Strategic context"
        plan.staff = [['insert'], ['here']]
        plan.budget = [['expected'], ['budget']]
        #plan.director_scd_comment = "Science director's comment"
        #plan.director_outputprogram_comment = "Output director's comment"
        plan.save()

        # Steven logs in and browses to the url of Bob's concept plan.
        self.create_preauthenticated_session(self.steven)
        url = reverse('admin:documents_conceptplan_change', args=(plan.id,))
        self.selenium.get("%s%s" % (self.live_server_url, url))
        self.wait_page_loaded()

        # TODO
        # There are no other endorsements attached to the document yet,
        # and the endorsements table indicates "No endorsements"
        #endorsements_text = self.selenium.find_element_by_css_selector(
        #    '#endorsements > tbody > td').text
        #self.assertEqual(endorsements_text, "No endorsements.")

        # He notes that there is a button for him to submit his endorsement
        # and he clicks the link which takes him to a new page.
        #button = self.selenium.find_element_by_id('add_endorsement')
        #self.assertEqual(button.text, 'Add')

        # He clicks the button, which should take him to a confirmation page.
        #button.click()
        #self.wait_page_loaded()

    def test_submitting_concept_plan_for_approval(self):
        """Test submitting the concept plan for approval.

        The SMT has decided the project fits in with SCD's strategic goals and
        approves the ConceptPlan. This should prompt the Directors of SCD and
        the respective output program for their comments and final approval
        from SCDD.
        """
        plan = self.project.documents.instance_of(ConceptPlan).get()

        plan.status = plan.STATUS_INREVIEW
        plan.summary = "Project summary"
        plan.outcome = "Expected project outcome"
        plan.collaborations = "Project collaborations"
        plan.strategic = "Strategic context"
        plan.staff = [['insert'], ['here']]
        plan.budget = [['expected'], ['budget']]
        plan.director_scd_comment = "Science director's comment"
        plan.director_outputprogram_comment = "Output director's comment"
        plan.save()

        self.create_preauthenticated_session(user=self.user)#usr=self.steven)

        # TODO Steven finds the document requiring his approval on the front page

        # Steven browses to the url of his concept plan.
        url = reverse('admin:documents_conceptplan_change', args=(plan.id,))
        self.selenium.get("%s%s" % (self.live_server_url, url))
        self.wait_page_loaded()

        # He checks that a button is available to submit his plan to be
        # approved.
        #approval_button = self.selenium.find_element_by_id('id_inapproval')
        #self.assertEqual(approval_button.text, 'Submit for approval')

        # He clicks the button, which should take him to a confirmation page.
        #approval_button.click()
        #self.wait_page_loaded()

        # He notes the confirmation page and confirms his desire to submit
        # his concept plan for review.
        #self.selenium.find_element_by_id('id_confirm').click()
        #self.wait_page_loaded()

        # His confirmation sends the system into a spin and it kicks the
        # concept plan into the state "Review requested". Success!
        #plan = self.project.documents.instance_of(ConceptPlan).get()
        #status = self.selenium.find_element_by_id('document_status').text
        #self.assertEqual(status, plan.get_status_display())


        # TODO: test PDF export
        # info = self.spp._meta.app_label, self.spp._meta.model_name
        # pdf_url = reverse('admin:%s_%s_download_pdf' % info, args=(self.spp.id,))
        # tex_url = reverse('admin:%s_%s_download_tex' % info, args=(self.spp.id,))
        
        # self.assert_200(pdf_url)
        # self.assert_200(tex_url)
        # self.assert_200(html_url)