"""Model tests for SDIS."""
from django.test import TestCase
from django.contrib.auth.models import Group
# from django_fsm.db.fields import TransitionNotAllowed

from pythia.models import Program
from pythia.documents.models import (
    Document, StudentReport, ConceptPlan, ProjectPlan,
    ProgressReport, ProjectClosure)
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

    def tearDown(self):
        """Destroy test objects after a test."""
        [m.delete for m in ProjectMembership.objects.all()]
        self.scp.delete()
        self.project.delete()
        self.superuser.delete()
        self.bob.delete()
        self.steven.delete()
        self.marge.delete()
        self.peter.delete()
        self.program.delete()

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
        print("The ConceptPlan is new and ready to be submitted.")
        scp = self.project.documents.instance_of(ConceptPlan).get()
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
                  self.project.__str__(), self.project.status, scp.status))
        scp.approve()
        print("Approvers have approved the ConceptPlan"
              " ({2}) on Project {0} ({1}).".format(
                  self.project.__str__(), self.project.status, scp.status))
        self.assertEqual(scp.status, Document.STATUS_APPROVED)

        print("Approving the ConceptPlan endorses the Project.")
        self.assertEqual(scp.project.status, Project.STATUS_PENDING)

        print("Endorsing the Project creates a ProjectPlan (SPP).")
        self.assertEqual(self.project.documents.instance_of(ProjectPlan).count(), 1)
        spp = self.project.documents.instance_of(ProjectPlan).get()
        self.assertEqual(spp.status, Document.STATUS_NEW)

        print("SPP can be submitted for review, no mandatory fields.")
        self.assertTrue(spp.can_seek_review())
        spp.seek_review()
        self.assertEqual(spp.status, Document.STATUS_INREVIEW)
        print("SPP cannot seek approval without BM and HC endorsement.")
        self.assertFalse(spp.can_seek_approval())

        print("SPP needs Biometrician's endorsement.")
        self.assertTrue(spp.bm_endorsement, Document.ENDORSEMENT_REQUIRED)
        self.assertFalse(spp.cleared_bm)
        spp.bm_endorsement = Document.ENDORSEMENT_GRANTED
        spp.save()
        self.assertTrue(spp.bm_endorsement, Document.ENDORSEMENT_GRANTED)
        self.assertTrue(spp.cleared_bm)

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

        print("SPP with BM and HC endorsement can seek approval")
        self.assertTrue(spp.can_seek_approval())
        spp.seek_approval()
        self.assertEqual(spp.status, Document.STATUS_INAPPROVAL)

        print("SPP needs AE's endorsement only if animals are involved.")
        print("SPP in approval not involving animals can be approved")
        self.assertEqual(spp.status, Document.STATUS_INAPPROVAL)
        self.assertFalse(spp.involves_animals)
        self.assertTrue(spp.cleared_ae)

        print("SPP in approval involving animals can not be approved "
              "without AE endorsement")
        spp.involves_animals = True
        spp.save()
        self.assertTrue(spp.involves_animals)
        self.assertFalse(spp.cleared_ae)
        self.assertTrue(spp.ae_endorsement, Document.ENDORSEMENT_REQUIRED)

        print("AE endorses SPP, SPP can be approved")
        spp.ae_endorsement = Document.ENDORSEMENT_GRANTED
        spp.save()
        self.assertEqual(spp.ae_endorsement, Document.ENDORSEMENT_GRANTED)
        self.assertTrue(spp.cleared_ae)

        print("SPP approval turns project ACTIVE")
        spp.approve()
        self.assertEqual(spp.status, Document.STATUS_APPROVED)
        print("Is self.project the same as spp.project?")
        self.assertEqual(self.project, spp.project)
        print("Is self.project.status the same as spp.project.status?")
        self.assertEqual(self.project.status, spp.project.status)
        print("Check that project is ACTIVE")
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

        print("Active projects can be suspended and brought back to ACTIVE")
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
        self.assertTrue(self.project.can_suspend())
        self.project.suspend()
        self.assertEqual(self.project.status, Project.STATUS_SUSPENDED)
        self.project.reactivate_suspended()
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

        print("Active projects can be terminated... they will be BACK")
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
        self.assertTrue(self.project.can_terminate())
        self.project.terminate()
        self.assertEqual(self.project.status, Project.STATUS_TERMINATED)
        self.project.reactivate_terminated()
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

        print("Active projects can be force-choked and resuscitated")
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
        self.project.force_complete()
        self.assertEqual(self.project.status, Project.STATUS_COMPLETED)
        self.project.reactivate()
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

        print("Request update")
        from datetime import datetime
        n = datetime.now()
        r = ARARReport.objects.create(year=self.project.year, date_open=n, date_closed=n)
        print("Created {0}".format(r.__str__()))
        self.project.request_update()
        self.assertEqual(self.project.status, Project.STATUS_UPDATE)
        self.assertEqual(self.project.documents.instance_of(ProgressReport).count(), 1)
        self.assertEqual(self.project.documents.instance_of(ProgressReport).get().status, Document.STATUS_NEW)
        print("Complete update")
        self.project.documents.instance_of(ProgressReport).get().seek_review()
        self.project.documents.instance_of(ProgressReport).get().seek_approval()
        self.project.documents.instance_of(ProgressReport).get().approve()
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

        print("Request closure")
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
        self.project.request_closure()
        print("Project should be in CLOSURE_REQUESTED")
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        print("Check for ProjectClosure document")
        print("Project should be in CLOSURE_REQUESTED")
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        self.assertEqual(self.project.documents.instance_of(ProjectClosure).count(), 1)
        self.assertEqual(self.project.documents.instance_of(ProjectClosure).get().status, Document.STATUS_NEW)
        print("Fast-track ProjectClosure document through review and approval")
        self.project.documents.instance_of(ProjectClosure).get().seek_review()
        self.project.documents.instance_of(ProjectClosure).get().seek_approval()
        self.project.documents.instance_of(ProjectClosure).get().approve()
        print("Check that ProjectClosure is approved")
        self.assertEqual(self.project.documents.instance_of(ProjectClosure).get().status, Document.STATUS_APPROVED)
        print("Check that project is STATUS_CLOSING")
        self.assertEqual(self.project.status, Project.STATUS_CLOSING)

        print("Request final update")
        self.project.request_update()
        self.assertEqual(self.project.status, Project.STATUS_FINAL_UPDATE)
        self.assertEqual(self.project.documents.instance_of(ProgressReport).count(), 2)
        self.assertEqual(self.project.documents.instance_of(ProgressReport).get().status, Document.STATUS_NEW)
        print("Complete update")
        self.project.documents.instance_of(ProgressReport).get().seek_review()
        self.project.documents.instance_of(ProgressReport).get().seek_approval()
        self.project.documents.instance_of(ProgressReport).get().approve()
        print("Approving final update completes project")
        self.assertEqual(self.project.status, Project.STATUS_COMPLETED)
        print("Full ScienceProject test walkthrough successfully completed.")

    def test_force_closure_updating_project(self):
        """Test force-closing an updating project.

        Ensure latest ProgressReport is removed and project is set to closure
        requested.
        """
        print("Create active project, request update")
        p = self.project
        p.status = Project.STATUS_ACTIVE
        p.save()
        self.assertEqual(p.status, Project.STATUS_ACTIVE)

        print("Create ARARReport so we can request updates")
        from datetime import datetime
        n = datetime.now()
        r = ARARReport.objects.create(year=p.year, date_open=n, date_closed=n)
        print("Creating ARAR {0}".format(r.__str__()))
        p.request_update()
        self.assertEqual(p.status, Project.STATUS_UPDATE)
        pr = p.documents.instance_of(ProgressReport).get()
        self.assertEqual(p.documents.instance_of(ProgressReport).count(), 1)
        self.assertEqual(pr.status, Document.STATUS_NEW)

        print("Force closure of project sets project to closure requested")
        p.force_closure()
        self.assertEqual(p.status, Project.STATUS_CLOSURE_REQUESTED)
        print("Force closure of project deletes latest projectplan")
        self.assertEqual(p.documents.instance_of(ProgressReport).count(), 0)

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


class CoreFunctionProjectModelTests(TestCase):
    """Test CoreFunction model methods, transitions, gate checks."""

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

    def test_studentproject_progressreport(self):
        """Test the life cycle of a StudentReport."""
        p = StudentProjectFactory.create()
        self.assertEqual(p.status, Project.STATUS_ACTIVE)
        from datetime import datetime
        n = datetime.now()
        r = ARARReport.objects.create(year=p.year, date_open=n, date_closed=n)
        print("Created {0}".format(r.__str__()))
        print("Request update")
        p.request_update()
        self.assertFalse(p.can_complete_update())
        pr = p.documents.instance_of(StudentReport).get()
        pr = StudentReport.objects.filter(project=p)[0]
        pr.seek_review()
        pr.seek_approval()
        pr.approve()
        self.assertEqual(pr.status, Document.STATUS_APPROVED)
        self.assertTrue(pr.project.status, Project.STATUS_ACTIVE)
