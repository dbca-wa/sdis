"""Model tests for SDIS."""
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import Group
# from django_fsm.db.fields import TransitionNotAllowed
from django.core.urlresolvers import reverse
from django.test import Client

from pythia.models import Program, programs_upload_to
from pythia.documents.models import (
    Document, StudentReport, ConceptPlan, ProjectPlan,
    ProgressReport, ProjectClosure)
from pythia.projects.models import (
    Project, ProjectMembership, projects_upload_to)
from pythia.reports.models import ARARReport
from .base import (BaseTestCase, ProjectFactory, ScienceProjectFactory,
                   CoreFunctionProjectFactory, CollaborationProjectFactory,
                   StudentProjectFactory, UserFactory, SuperUserFactory,
                   ProgramFactory)


def avail_tx(u, tx, obj):
    """Return whether a user has transition available on an obj.

    Arguments:

        u   User instance (User)
        tx  transition name (String)
        obj An object with django-fsm transitions

    Returns:
        boolean Whether a user can run transition on an object.
    """
    return tx in [t.name for t in obj.get_available_user_status_transitions(u)]


# class UserModelTests(TestCase):
#     """User model tests."""
#
#     def test_user_is_valid_with_email_only(self):
#         """Test that a user profile is valid with an email only.
#
#         A user profile must be valid with an email only.
#         Everything else is a bonus!
#         """
#         print("TODO")
#         pass  # TODO
# TODO portfolio: make projects to fall into/out of each category of
# tasklist/portfolio for users of each role

class ProgramModelTests(BaseTestCase):
    "Base program tests."

    def setUp(self):
        """Create a Program."""
        self.steven = UserFactory.create(
            username='steven', first_name='Steven', last_name='Stevenson')
        self.marge = UserFactory.create(
            username='marge', first_name='Marge', last_name='Simpson')
        self.program = ProgramFactory.create(
            creator=self.marge, program_leader=self.steven)

    def tearDown(self):
        """Destroy test objects after a test."""
        self.program.delete()
        self.steven.delete()
        self.marge.delete()

    def test_programs_upload_to(self):
        """Test that program image filename gets sanitised enough for Latex."""
        filename_crazy = "some batshit.crazy.filename.jpg"
        filename_sane = "some_batshit_crazy_filename.jpg"
        upload_path_calculated = programs_upload_to(
            self.program, filename_crazy)
        upload_path_handbuilt = "programs/{0}/{1}".format(
            self.program.slug,
            filename_sane
            )
        self.assertEqual(upload_path_calculated, upload_path_handbuilt)

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
        * Matt (Biometrician), Kevin (Herbarium Curator), Annie (Animal Ethics),
          Flo (Data Manager) are representatives of special roles.
        """
        self.smt, created = Group.objects.get_or_create(name='SMT')
        self.scd, created = Group.objects.get_or_create(name='SCD')
        self.bm, created = Group.objects.get_or_create(name='BM')
        self.hc, created = Group.objects.get_or_create(name='HC')
        self.ae, created = Group.objects.get_or_create(name='AE')
        self.dm, created = Group.objects.get_or_create(name='DM')
        self.users, created = Group.objects.get_or_create(name='Users')
        from pythia.documents.utils import grant_special_role_permissions
        grant_special_role_permissions()

        self.superuser = SuperUserFactory.create(
            username='admin', first_name="Admin", last_name="Superuser")
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
        self.matt = UserFactory.create(
            username='matt', first_name='Matt', last_name='Williamson')
        self.matt.groups.add(self.bm)
        self.kevin = UserFactory.create(
            username='kevin', first_name='Kevin', last_name='Thielson')
        self.kevin.groups.add(self.hc)
        self.annie = UserFactory.create(
            username='annie', first_name='Annie', last_name='Ethicsson')
        self.annie.groups.add(self.ae)
        self.flo = UserFactory.create(
            username='flo', first_name='Flojo', last_name='Datason')
        self.flo.groups.add(self.dm)
        self.peter = UserFactory.create(
            username='peter', first_name='Peter', last_name='Peterson')
        # Team roles
        self.techo = UserFactory.create(
            username='techo', first_name='Technical', last_name='Officer')

        self.external_peer = UserFactory.create(
            username='externalpeer', first_name='External', last_name='Peer')
        self.consulted_peer = UserFactory.create(
            username='consultedpeer', first_name='Consulted', last_name='Peer')
        self.academic = UserFactory.create(
            username='academic', first_name='Anonymous', last_name='Academic')
        self.student = UserFactory.create(
            username='student', first_name='Supervised', last_name='Student')
        self.collaborator = UserFactory.create(
            username='collab', first_name='External', last_name='Collaborator')
        self.group = UserFactory.create(
            username='group', first_name='External', last_name='Group',
            is_group=True, group_name='Group Name')

        self.program = ProgramFactory.create(
            creator=self.marge, program_leader=self.steven)

        self.project = ScienceProjectFactory.create(
            # creator=self.bob,
            program=self.program,
            # data_custodian=self.bob, site_custodian=self.bob,
            project_owner=self.bob)

        # Bob should automatically be a team member

        # John will join as ROLE_RESEARCH_SCIENTIST later in a test method

        ProjectMembership.objects.create(
            project=self.project,
            user=self.techo,
            position=300,
            role=ProjectMembership.ROLE_TECHNICAL_OFFICER)

        ProjectMembership.objects.create(
            project=self.project,
            user=self.external_peer,
            position=400,
            role=ProjectMembership.ROLE_EXTERNAL_PEER)

        ProjectMembership.objects.create(
            project=self.project,
            user=self.consulted_peer,
            position=500,
            role=ProjectMembership.ROLE_CONSULTED_PEER)

        ProjectMembership.objects.create(
            project=self.project,
            user=self.academic,
            position=600,
            role=ProjectMembership.ROLE_ACADEMIC_SUPERVISOR)

        ProjectMembership.objects.create(
            project=self.project,
            user=self.student,
            position=700,
            role=ProjectMembership.ROLE_SUPERVISED_STUDENT)

        ProjectMembership.objects.create(
            project=self.project,
            user=self.collaborator,
            position=800,
            role=ProjectMembership.ROLE_EXTERNAL_COLLABORATOR)

        ProjectMembership.objects.create(
            project=self.project,
            user=self.group,
            position=900,
            role=ProjectMembership.ROLE_GROUP)

        self.scp = self.project.documents.instance_of(ConceptPlan).get()

        self.client = Client()
        self.url = reverse('admin:documents_conceptplan_change',
                           args=(self.scp.id,))
        self.tx_url = 'admin:documents_conceptplan_transition?transition={0}'

    def tearDown(self):
        """Destroy test objects after a test."""
        self.scp.delete()
        self.project.delete()
        self.superuser.delete()
        self.bob.delete()
        self.steven.delete()
        self.marge.delete()
        self.peter.delete()
        self.program.delete()

    def test_project_upload_to(self):
        """Test that project image filename gets sanitised enough for Latex."""
        filename_crazy = "some batshit.crazy.filename.jpg"
        filename_sane = "some_batshit_crazy_filename.jpg"
        upload_path_calculated = projects_upload_to(
            self.project, filename_crazy)
        upload_path_handbuilt = "projects/{0}-{1}/{2}".format(
            self.project.year,
            self.project.number,
            filename_sane
            )
        self.assertEqual(upload_path_calculated, upload_path_handbuilt)

    def test_team_lists(self):
        """Test Project team lists order and membership."""
        tlp = self.project.team_list_plain
        print("\n  Team list plain shall only show staff: {0}".format(tlp))
        self.assertTrue(self.bob.last_name in tlp)
        self.assertTrue(self.techo.last_name in tlp)
        self.assertFalse(self.external_peer.last_name in tlp)
        self.assertFalse(self.consulted_peer.last_name in tlp)
        self.assertFalse(self.academic.last_name in tlp)
        self.assertFalse(self.student.last_name in tlp)
        self.assertFalse(self.collaborator.last_name in tlp)
        self.assertFalse(self.group.group_name in tlp)

        sslp = self.project.get_supervising_scientist_list_plain()
        print("  Sup Sci list plain shall only show Sup Sci: {0}".format(sslp))
        self.assertTrue(self.bob.last_name in sslp)
        self.assertFalse(self.techo.last_name in sslp)
        self.assertFalse(self.external_peer.last_name in sslp)
        self.assertFalse(self.consulted_peer.last_name in sslp)
        self.assertFalse(self.academic.last_name in sslp)
        self.assertFalse(self.student.last_name in sslp)
        self.assertFalse(self.collaborator.last_name in sslp)
        self.assertFalse(self.group.group_name in sslp)

        ts = self.project.team_students
        print("  Team Students shall only show Students: {0}".format(ts))
        self.assertFalse(self.bob.last_name in ts)
        self.assertFalse(self.techo.last_name in ts)
        self.assertFalse(self.external_peer.last_name in ts)
        self.assertFalse(self.consulted_peer.last_name in ts)
        self.assertFalse(self.academic.last_name in ts)
        self.assertTrue(self.student.last_name in ts)
        self.assertFalse(self.collaborator.last_name in ts)
        self.assertFalse(self.group.group_name in ts)

        tl = self.project.team_list
        tln = ", ".join([x[1] for x in tl])
        # m.get_role_display(), m.user.fullname, m.time_allocation
        print("  Team list shall only contain staff roles: {0}".format(tln))
        self.assertTrue(self.bob.last_name in tln)
        self.assertTrue(self.techo.last_name in tln)
        self.assertFalse(self.external_peer.last_name in tln)
        self.assertFalse(self.consulted_peer.last_name in tln)
        self.assertFalse(self.academic.last_name in tln)
        self.assertFalse(self.student.last_name in tln)
        self.assertFalse(self.collaborator.last_name in tln)
        self.assertFalse(self.group.group_name in tln)

    def test_everyone_can_view_conceptplan(self):
        """Test that everyone can view the ConceptPlan."""
        # get ConceptPlan detail
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_new_science_project(self):
        """A new ScienceProject has one new ConceptPlan and only setup tx."""
        p = self.project

        print("\n  A new ScienceProject must be of STATUS_NEW.")
        self.assertEqual(p.status, Project.STATUS_NEW)

        print("  A new SP has exactly one document, a ConceptPlan.")
        self.assertEqual(p.documents.count(), 1)
        self.assertEqual(p.documents.instance_of(ConceptPlan).count(), 1)

        print("  A new SP has only setup tx until the SCP is approved.")
        avail_tx = [t.name for t in p.get_available_status_transitions()]
        self.assertEqual(len(avail_tx), 0)

    def test_conceptplan_permissions(self):
        """Test expected ConceptPlan permissions for transitions.

        * All users should be able to view.
        * Only involved staff (submitters, reviewers, approvers)
          should be able to change and submit.
        * Only SMT members should be able to review.
        * Only SCD members should be able to approve.
        """
        print("\n  Only project team members like Bob, reviewers and approvers "
              "can submit the ConceptPlan.")
        self.assertTrue(avail_tx(self.bob, 'seek_review', self.scp))
        self.assertTrue(avail_tx(self.steven, 'seek_review', self.scp))
        self.assertTrue(avail_tx(self.fran, 'seek_review', self.scp))
        self.assertTrue(avail_tx(self.marge, 'seek_review', self.scp))

        print("  John is not on the team and has no permission to submit.")
        self.assertFalse(avail_tx(self.john, 'seek_review', self.scp))

        print("  Peter is not on the team and has no permission to submit.")
        self.assertFalse(avail_tx(self.peter, 'seek_review', self.scp))

        print("  John joins the project team.")
        ProjectMembership.objects.create(
            project=self.project,
            user=self.john,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        print("  John is now on the team and has permission to submit.")
        self.assertTrue(avail_tx(self.john, 'seek_review', self.scp))

        print("  Fast-track ConceptPlan to INREVIEW.")
        self.scp.seek_review()
        self.assertEqual(self.scp.status, Document.STATUS_INREVIEW)

        print("  Submitters can recall document from review.")
        self.assertTrue(avail_tx(self.bob, 'recall', self.scp))

        print("  Only reviewers can seek_approval or seek author revision.")
        self.assertTrue(avail_tx(self.steven, 'seek_approval', self.scp))
        self.assertTrue(
            avail_tx(self.steven, 'request_revision_from_authors', self.scp))

        print("  Fast-track ConceptPlan to INAPPROVAL.")
        self.scp.seek_approval()
        self.assertEqual(self.scp.status, Document.STATUS_INAPPROVAL)
        self.assertEqual(
            set([tx.name for tx in
                 self.scp.get_available_user_status_transitions(self.marge)]),
            set(['approve',
                 'request_reviewer_revision',
                 'request_author_revision']))

        self.assertEqual(
            [tx.name for tx in
             self.scp.get_available_user_status_transitions(self.steven)],
            ['recall_approval'])

        self.assertEqual(
            [tx.name for tx in
             self.scp.get_available_user_status_transitions(self.fran)],
            ['recall_approval'])

        self.assertEqual(
            [tx.name for tx in
             self.scp.get_available_user_status_transitions(self.bob)], [])

        self.assertEqual(
            [tx.name for tx in
             self.scp.get_available_user_status_transitions(self.john)], [])

        self.assertEqual(
            [tx.name for tx in
             self.scp.get_available_user_status_transitions(self.peter)], [])

        print("  Fast-track ConceptPlan to APPROVED.")
        self.scp.approve()
        self.assertEqual(self.scp.status, Document.STATUS_APPROVED)
        print("  Only approvers can reset the document.")
        self.assertTrue(avail_tx(self.marge, 'reset', self.scp))
        self.assertFalse(avail_tx(self.steven, 'reset', self.scp))
        self.assertFalse(avail_tx(self.fran, 'reset', self.scp))
        self.assertFalse(avail_tx(self.bob, 'reset', self.scp))
        self.assertFalse(avail_tx(self.john, 'reset', self.scp))
        self.assertFalse(avail_tx(self.peter, 'reset', self.scp))

    def test_scienceproject_endorsement(self):
        """Test all possible transitions in a ScienceProject's life cycle.

        Focus on objects being created, gate checks.
        Ignoring user permissions.
        """
        print("\n  The ConceptPlan is new and ready to be submitted.")
        scp = self.project.documents.instance_of(ConceptPlan).get()
        self.assertTrue(scp.status == Document.STATUS_NEW)
        self.assertTrue(scp.can_seek_review())

        print("  The team submits for review")
        scp.seek_review()
        # The SCP sits with the Program Leader now
        self.assertTrue(scp.status == Document.STATUS_INREVIEW)
        self.assertTrue(scp.can_seek_approval())

        print("  The team recalls the document from review.")
        scp.recall()
        self.assertTrue(scp.status == Document.STATUS_NEW)

        print("  The team re-submits the doc for review.")
        scp.seek_review()
        self.assertTrue(scp.status == Document.STATUS_INREVIEW)
        self.assertTrue(scp.can_seek_approval())

        print("  The reviewer request revision from authors.")
        scp.request_revision_from_authors()
        self.assertTrue(scp.status == Document.STATUS_NEW)

        print("  Authors seek review again.")
        scp.seek_review()
        print("  Reviewer seeks approval.")
        scp.seek_approval()
        self.assertTrue(scp.status == Document.STATUS_INAPPROVAL)
        self.assertTrue(scp.can_approve())

        print("  Approvers approve the ConceptPlan "
              "({2}) on Project {0} ({1}).".format(
                  self.project.__str__(), self.project.status, scp.status))
        scp.approve()
        print("  Approvers have approved the ConceptPlan"
              " ({2}) on Project {0} ({1}).".format(
                  self.project.__str__(), self.project.status, scp.status))
        self.assertEqual(scp.status, Document.STATUS_APPROVED)

        print("  Approving the ConceptPlan endorses the Project.")
        self.assertEqual(scp.project.status, Project.STATUS_PENDING)

        print("  Endorsing the Project creates a ProjectPlan (SPP).")
        self.assertEqual(
            self.project.documents.instance_of(ProjectPlan).count(), 1)
        spp = self.project.documents.instance_of(ProjectPlan).get()
        self.assertEqual(spp.status, Document.STATUS_NEW)

    def test_scienceproject_approval(self):
        """Test ScienceProject approval workflow.

        Team > reviewers (endorsements) > approved.
        """
        project = ScienceProjectFactory.create(
            creator=self.bob,
            modifier=self.bob,
            program=self.program,
            # data_custodian=self.bob, site_custodian=self.bob,
            project_owner=self.bob)

        ProjectMembership.objects.create(
            project=project,
            user=self.bob,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        scp = project.documents.instance_of(ConceptPlan).get()
        scp.seek_review()
        scp.seek_approval()
        scp.approve()
        project = scp.project
        self.assertEqual(project.status, Project.STATUS_PENDING)
        print("\n  Endorsing the Project creates a ProjectPlan (SPP).")
        self.assertEqual(project.documents.instance_of(ProjectPlan).count(), 1)
        spp = project.documents.instance_of(ProjectPlan).get()
        self.assertEqual(spp.status, Document.STATUS_NEW)

        print("  SPP can be submitted for review, no mandatory fields.")
        self.assertTrue(spp.can_seek_review())
        spp.seek_review()
        self.assertEqual(spp.status, Document.STATUS_INREVIEW)

        print("  SPP skips third approval tier INAPPROVAL.")
        self.assertFalse(avail_tx(self.steven, 'seek_approval', spp))
        self.assertFalse(avail_tx(self.fran, 'seek_approval', spp))
        self.assertFalse(avail_tx(self.marge, 'seek_approval', spp))

        print("  BM has change permission to add endorsenemt to SPP")
        self.assertTrue(self.matt.has_perm("documents.change_projectplan"))

        print("  HC has change permission to add endorsenemt to SPP")
        self.assertTrue(self.kevin.has_perm("documents.change_projectplan"))

        print("  AE has change permission to add endorsenemt to SPP")
        self.assertTrue(self.annie.has_perm("documents.change_projectplan"))

        print("  DM has change permission to add endorsenemt to SPP")
        self.assertTrue(self.flo.has_perm("documents.change_projectplan"))

        print("  SPP cannot be approved without required endorsement.")
        self.assertFalse(spp.can_approve())

        print("  SPP in review cannot be approved without BM endorsement.")
        self.assertTrue(spp.bm_endorsement, Document.ENDORSEMENT_REQUIRED)
        self.assertFalse(spp.cleared_bm)
        spp.bm_endorsement = Document.ENDORSEMENT_GRANTED
        spp.save()
        self.assertTrue(spp.bm_endorsement, Document.ENDORSEMENT_GRANTED)
        self.assertTrue(spp.cleared_bm)

        print("  SPP in review not involving plants can be approved without HC endorsement.")
        self.assertFalse(spp.involves_plants)
        self.assertTrue(spp.cleared_hc)

        print("  SPP in review involving plants can not be approved without HC endorsement.")
        spp.involves_plants = True
        spp.save()
        self.assertTrue(spp.involves_plants)
        self.assertFalse(spp.cleared_hc)
        self.assertTrue(spp.hc_endorsement, Document.ENDORSEMENT_REQUIRED)

        print("  SPP in review involving plants can be approved after HC endorsement.")
        spp.hc_endorsement = Document.ENDORSEMENT_GRANTED
        spp.save()
        self.assertTrue(spp.hc_endorsement, Document.ENDORSEMENT_GRANTED)
        self.assertTrue(spp.cleared_hc)

        print("  SPP in review not involving animals can be approved without AE endorsement.")
        self.assertEqual(spp.status, Document.STATUS_INREVIEW)
        self.assertFalse(spp.involves_animals)
        self.assertTrue(spp.cleared_ae)

        print("  SPP in review involving animals can not be approved without AE endorsement.")
        spp.involves_animals = True
        spp.save()
        self.assertTrue(spp.involves_animals)
        self.assertTrue(spp.ae_endorsement, Document.ENDORSEMENT_REQUIRED)
        self.assertFalse(spp.cleared_ae)

        print("  SPP in review involving animals can be approved after AE endorsement.")
        spp.ae_endorsement = Document.ENDORSEMENT_GRANTED
        spp.save()
        self.assertEqual(spp.ae_endorsement, Document.ENDORSEMENT_GRANTED)
        self.assertTrue(spp.cleared_ae)

        print("  SPP approval turns project ACTIVE")
        spp.approve()
        self.assertEqual(spp.status, Document.STATUS_APPROVED)
        print("  Is self.project the same as spp.project?")
        self.assertEqual(project.id, spp.project.id)
        print("  Is self.project.status the same as spp.project.status?")
        # self.assertEqual(self.project.status, spp.project.status) # it's not!
        # spp.project was changed by spp.approve, self.project wasn't
        print("  Check that project is ACTIVE")
        self.assertEqual(spp.project.status, Project.STATUS_ACTIVE)

    def test_scienceproject_update(self):
        """Test the update workflow of a ScienceProject."""
        self.project.status = Project.STATUS_ACTIVE
        self.project.save()

        print("\n  Request update")
        from datetime import datetime
        n = datetime.now()
        r = ARARReport.objects.create(
            year=self.project.year, date_open=n, date_closed=n)
        print("  Created {0}".format(r.__str__()))
        self.project.request_update()
        self.project.save()

        pr = self.project.documents.instance_of(ProgressReport).get()

        self.assertEqual(self.project.status, Project.STATUS_UPDATE)
        self.assertEqual(
            self.project.documents.instance_of(ProgressReport).count(), 1)
        self.assertEqual(pr.status, Document.STATUS_NEW)
        print("  Complete update")
        pr.seek_review()
        pr.seek_approval()
        pr.approve()
        self.project = pr.project
        self.project.save()
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

    def test_scienceproject_cancel_update(self):
        """Test force closure during update of a ScienceProject."""
        self.project.status = Project.STATUS_ACTIVE
        self.project.save()

        print("\n  Request update")
        from datetime import datetime
        n = datetime.now()
        r = ARARReport.objects.create(
            year=self.project.year, date_open=n, date_closed=n)
        print("  Created {0}".format(r.__str__()))
        self.project.request_update()
        self.project.save()

        pr = self.project.documents.instance_of(ProgressReport).get()

        self.assertEqual(self.project.status, Project.STATUS_UPDATE)
        self.assertEqual(
            self.project.documents.instance_of(ProgressReport).count(), 1)
        self.assertEqual(pr.status, Document.STATUS_NEW)

        print("  force_closure is available to reviewers_approvers")
        self.assertTrue(avail_tx(self.marge, 'force_closure', self.project))
        self.assertTrue(avail_tx(self.steven, 'force_closure', self.project))
        self.assertTrue(avail_tx(self.fran, 'force_closure', self.project))
        self.assertFalse(avail_tx(self.bob, 'force_closure', self.project))
        self.assertFalse(avail_tx(self.john, 'force_closure', self.project))
        self.assertFalse(avail_tx(self.peter, 'force_closure', self.project))

        print("  Run force_closure on {0}".format(self.project.debugname))
        self.project.force_closure()
        self.project.save()
        print("  {0} should be CLOSURE_REQUESTED".format(self.project.debugname))
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        print("  There should be one NEW ProjectClosure")
        pc = self.project.documents.instance_of(ProjectClosure).get()
        self.assertEqual(
            self.project.documents.instance_of(ProjectClosure).count(), 1)
        print("  There should be zero ProgressReports")
        self.assertEqual(pc.status, Document.STATUS_NEW)
        self.assertEqual(
            self.project.documents.instance_of(ProgressReport).count(), 0)

    def test_scienceproject_closure(self):
        """Test the default closure workflow of a ScienceProject."""
        self.project.status = Project.STATUS_ACTIVE
        self.project.save()

        print("\n  Request closure")
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
        self.project.request_closure()
        self.project.save()
        print("  Project should be in CLOSURE_REQUESTED")
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        print("  Check for ProjectClosure document")
        self.assertEqual(
            self.project.documents.instance_of(ProjectClosure).count(), 1)
        pc = self.project.documents.instance_of(ProjectClosure).get()
        self.assertEqual(pc.status, Document.STATUS_NEW)
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        print("  Fast-track ProjectClosure document through review and approval")
        pc.seek_review()
        pc.seek_approval()
        pc.approve()
        print("  Check that {0} is approved".format(pc.debugname))
        self.assertEqual(pc.status, Document.STATUS_APPROVED)
        self.project = pc.project    # NOTE pc.project has latest change
        self.project.save()          # NOTE sync to db
        self.assertEqual(self.project.status, Project.STATUS_CLOSING)

        print("  Create ARAR")
        arar = ARARReport.objects.create(
            year=self.project.year,
            creator=self.marge,
            date_open=datetime.now(),
            date_closed=datetime.now())

        print("  Request final update")
        self.project.request_final_update(arar)
        self.project.save()
        self.assertEqual(self.project.status, Project.STATUS_FINAL_UPDATE)
        print("  Check that there's exactly one ProgressReport.")
        self.assertEqual(
            self.project.documents.instance_of(ProgressReport).count(), 1)
        pr = self.project.documents.instance_of(ProgressReport).get()
        self.assertEqual(pr.status, Document.STATUS_NEW)
        print("  Complete update by fast-tracking ProgressReport approval.")
        pr.seek_review()
        pr.seek_approval()
        pr.approve()
        self.project = pr.project  # pr.project has latest change in memory
        self.project.save()
        print("  Approving final update completes project")
        self.assertEqual(self.project.status, Project.STATUS_COMPLETED)
        print("  Full ScienceProject test walkthrough successfully completed.")

    def test_scienceproject_force_closure(self):
        """Test the force-closure workflow of a ScienceProject."""
        self.project.status = Project.STATUS_ACTIVE
        self.project.save()

        print("\n  Request closure with goal closure without process")
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
        self.project.request_closure()
        self.project.save()
        print("  Project should be in CLOSURE_REQUESTED")
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        print("  Check for ProjectClosure document")
        self.assertEqual(
            self.project.documents.instance_of(ProjectClosure).count(), 1)
        pc = self.project.documents.instance_of(ProjectClosure).get()
        self.assertEqual(pc.status, Document.STATUS_NEW)
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        # Set project to force_closure
        pc.goal = ProjectClosure.STATUS_FORCE_COMPLETED
        pc.save()
        print("  Fast-track ProjectClosure document through review and approval")
        pc.seek_review()
        pc.seek_approval()
        pc.approve()
        print("  Check that {0} is approved".format(pc.debugname))
        self.assertEqual(pc.status, Document.STATUS_APPROVED)
        self.project = pc.project    # NOTE pc.project has latest change
        self.project.save()          # NOTE sync to db
        print("  Project must be in STATUS_COMPLETED")
        self.assertEqual(self.project.status, Project.STATUS_COMPLETED)

    def test_scienceproject_suspend(self):
        """Test the suspending workflow of a ScienceProject."""
        self.project.status = Project.STATUS_ACTIVE
        self.project.save()

        print("\n  Request closure with goal suspended")
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
        self.project.request_closure()
        self.project.save()
        print("  Project should be in CLOSURE_REQUESTED")
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        print("  Check for ProjectClosure document")
        self.assertEqual(
            self.project.documents.instance_of(ProjectClosure).count(), 1)
        pc = self.project.documents.instance_of(ProjectClosure).get()
        self.assertEqual(pc.status, Document.STATUS_NEW)
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        # Set project to force_closure
        pc.goal = ProjectClosure.STATUS_SUSPENDED
        pc.save()
        print("  Fast-track ProjectClosure document through review and approval")
        pc.seek_review()
        pc.seek_approval()
        pc.approve()
        print("  Check that {0} is approved".format(pc.debugname))
        self.assertEqual(pc.status, Document.STATUS_APPROVED)
        self.project = pc.project    # NOTE pc.project has latest change
        self.project.save()          # NOTE sync to db
        print("  Project must be in STATUS_COMPLETED")
        self.assertEqual(self.project.status, Project.STATUS_SUSPENDED)

    def test_scienceproject_terminate(self):
        """Test the termination workflow of a ScienceProject."""
        self.project.status = Project.STATUS_ACTIVE
        self.project.save()

        print("\n  Request closure with goal terminated")
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
        self.project.request_closure()
        self.project.save()
        print("  Project should be in CLOSURE_REQUESTED")
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        print("  Check for ProjectClosure document")
        self.assertEqual(
            self.project.documents.instance_of(ProjectClosure).count(), 1)
        pc = self.project.documents.instance_of(ProjectClosure).get()
        self.assertEqual(pc.status, Document.STATUS_NEW)
        self.assertEqual(self.project.status, Project.STATUS_CLOSURE_REQUESTED)
        # Set project to force_closure
        pc.goal = ProjectClosure.STATUS_TERMINATED
        pc.save()
        print("  Fast-track ProjectClosure document through review and approval")
        pc.seek_review()
        pc.seek_approval()
        pc.approve()
        print("  Check that {0} is approved".format(pc.debugname))
        self.assertEqual(pc.status, Document.STATUS_APPROVED)
        self.project = pc.project    # NOTE pc.project has latest change
        self.project.save()          # NOTE sync to db
        print("  Project must be in STATUS_COMPLETED")
        self.assertEqual(self.project.status, Project.STATUS_TERMINATED)

    def test_reset_conceptplan_on_pending_scienceproject(self):
        """Resetting an approved SCP resets SCP and project to NEW."""
        print("\n  Fast-forward SP to pending.")
        scp = self.project.documents.instance_of(ConceptPlan).get()
        scp.seek_review()
        scp.seek_approval()
        scp.approve()
        self.project = scp.project
        self.project.save()
        self.assertEqual(scp.status, Document.STATUS_APPROVED)
        scp.reset()
        scp.save()
        self.project = scp.project
        self.project.save()
        print("  After reset, both ConceptPlan and Project must be STATUS_NEW")
        self.assertEqual(scp.status, Document.STATUS_NEW)
        self.assertEqual(self.project.status, Project.STATUS_NEW)
        print("  Project setup should never spawn a second ConceptPlan")
        self.assertEqual(
            self.project.documents.instance_of(ConceptPlan).count(), 1)


class CoreFunctionProjectModelTests(TestCase):
    """Test CoreFunction model methods, transitions, gate checks.

    As both SP and CF inherit the same code and behaviour from Project,
    the detailed tests for SP won't require duplication here.

    The tests here are canary tests.
    """

    def setUp(self):
        """Create a CF and users for all roles.

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
        from pythia.documents.utils import grant_special_role_permissions
        grant_special_role_permissions()

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

        self.program = ProgramFactory.create(
            creator=self.marge, program_leader=self.steven)

        self.project = CoreFunctionProjectFactory.create(
            creator=self.bob,
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

    def new_CF_is_active(self):
        """A new CoreFunction has STATUS_ACTIVE immediately."""
        u = UserFactory.create()
        p = CoreFunctionProjectFactory.create(creator=u, project_owner=u)
        self.assertEqual(p.status, Project.STATUS_ACTIVE)
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

    def new_CF_has_conceptplan(self):
        """A new CoreFunction has one doc, a ConceptPlan."""
        self.assertEqual(self.project.documents.count(), 1)
        self.assertEqual(
            self.project.documents.instace_of(ConceptPlan).count(), 1)


class CollaborationProjectModelTests(TestCase):
    """CollaborationProject tests."""

    def setUp(self):
        """Create a StudentProject and users."""
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

        self.program = ProgramFactory.create(
            creator=self.marge, program_leader=self.steven)

        self.project = CollaborationProjectFactory.create(
            creator=self.bob,
            modifier=self.bob,
            program=self.program,
            # data_custodian=self.bob, site_custodian=self.bob,
            project_owner=self.bob)

        ProjectMembership.objects.create(
            project=self.project,
            user=self.bob,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

    def tearDown(self):
        """Destroy test objects after a test."""
        [m.delete for m in ProjectMembership.objects.all()]
        self.project.delete()
        self.superuser.delete()
        self.bob.delete()
        self.steven.delete()
        self.marge.delete()
        self.peter.delete()
        self.program.delete()

    def test_new_collaboration_project(self):
        """A new CollaborationProject is ACTIVE.

        It does not require an approval process.
        """
        project = CollaborationProjectFactory.create()
        self.assertEqual(project.status, Project.STATUS_ACTIVE)
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

    def test_complete_active_collaborationproject(self):
        """Test complete of an active CollaborationProject."""
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

        print("  complete is available to all_involved")
        self.assertTrue(avail_tx(self.marge, 'complete', self.project))
        self.assertTrue(avail_tx(self.steven, 'complete', self.project))
        self.assertTrue(avail_tx(self.fran, 'complete', self.project))
        self.assertTrue(avail_tx(self.bob, 'complete', self.project))
        self.assertFalse(avail_tx(self.john, 'complete', self.project))
        self.assertFalse(avail_tx(self.peter, 'complete', self.project))

        print("  Run complete on {0}".format(self.project.debugname))
        self.project.complete()
        self.project.save()
        print("  {0} should be COMPLETED".format(self.project.debugname))
        self.assertEqual(self.project.status, Project.STATUS_COMPLETED)


class StudentProjectModelTests(TestCase):
    """StudentProject model tests."""

    def setUp(self):
        """Create a StudentProject and users."""
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

        self.program = ProgramFactory.create(
            creator=self.marge, program_leader=self.steven)

        self.project = StudentProjectFactory.create(
            creator=self.bob,
            modifier=self.bob,
            program=self.program,
            # data_custodian=self.bob, site_custodian=self.bob,
            project_owner=self.bob)

        ProjectMembership.objects.create(
            project=self.project,
            user=self.bob,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

    def tearDown(self):
        """Destroy test objects after a test."""
        [m.delete for m in ProjectMembership.objects.all()]
        self.project.delete()
        self.superuser.delete()
        self.bob.delete()
        self.steven.delete()
        self.marge.delete()
        self.peter.delete()
        self.program.delete()

    def test_new_student_project(self):
        """A new STP has no approval process and is ACTIVE."""
        project = StudentProjectFactory.create()
        self.assertEqual(project.status, Project.STATUS_ACTIVE)
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

    def test_studentproject_progressreport(self):
        """Test the update workflow of a StudentReport."""
        from datetime import datetime
        n = datetime.now()
        r = ARARReport.objects.create(
            year=self.project.year, creator=self.marge,
            date_open=n, date_closed=n)
        print("  Created {0}".format(r.__str__()))
        print("  Request update")
        self.project.request_update()
        self.project.save()
        self.assertEqual(StudentReport.objects.count(), 1)
        self.assertEqual(self.project.status, Project.STATUS_UPDATE)
        pr = self.project.documents.instance_of(StudentReport).get()
        pr.seek_review()
        pr.seek_approval()
        pr.approve()
        self.assertEqual(pr.status, Document.STATUS_APPROVED)
        self.project = pr.project
        self.project.save()
        self.assertTrue(self.project.status, Project.STATUS_ACTIVE)

    def test_force_closure_updating_studentproject(self):
        """Test force closure of updating studentproject."""
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)
        from datetime import datetime
        n = datetime.now()
        r = ARARReport.objects.create(
            year=self.project.year, date_open=n, date_closed=n)
        print("\n  Created {0}".format(r.__str__()))
        print("  Request update")
        self.project.request_update()
        self.project.save()
        self.assertEqual(StudentReport.objects.count(), 1)
        self.assertEqual(self.project.status, Project.STATUS_UPDATE)

        print("  force_closure is available to all_involved")
        self.assertTrue(avail_tx(self.marge, 'force_closure', self.project))
        self.assertTrue(avail_tx(self.steven, 'force_closure', self.project))
        self.assertTrue(avail_tx(self.fran, 'force_closure', self.project))
        self.assertTrue(avail_tx(self.bob, 'force_closure', self.project))
        self.assertFalse(avail_tx(self.john, 'force_closure', self.project))
        self.assertFalse(avail_tx(self.peter, 'force_closure', self.project))

        print("  Run force_closure on {0}".format(self.project.debugname))
        self.project.force_closure()
        self.project.save()
        print("  {0} should be COMPLETED".format(self.project.debugname))
        self.assertEqual(self.project.status, Project.STATUS_COMPLETED)
        print("  There should be zero ProgressReports")
        self.assertEqual(
            self.project.documents.instance_of(ProgressReport).all().count(),
            0)

    def test_complete_active_studentproject(self):
        """Test complete of an active StudentProject."""
        self.assertEqual(self.project.status, Project.STATUS_ACTIVE)

        print("\n  complete is available to all_involved")
        self.assertTrue(avail_tx(self.marge, 'complete', self.project))
        self.assertTrue(avail_tx(self.steven, 'complete', self.project))
        self.assertTrue(avail_tx(self.fran, 'complete', self.project))
        self.assertTrue(avail_tx(self.bob, 'complete', self.project))
        self.assertFalse(avail_tx(self.john, 'complete', self.project))
        self.assertFalse(avail_tx(self.peter, 'complete', self.project))

        print("  Run complete on {0}".format(self.project.debugname))
        self.project.complete()
        self.project.save()
        print("  {0} should be COMPLETED".format(self.project.debugname))
        self.assertEqual(self.project.status, Project.STATUS_COMPLETED)


class ARARReportModelTests(TestCase):
    """ARARReport model tests."""

    def setUp(self):
        """Create one of each project type and users."""
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

        self.program = ProgramFactory.create(program_leader=self.steven)

        self.sp = ScienceProjectFactory.create(
            creator=self.bob,
            program=self.program,
            # data_custodian=self.bob, site_custodian=self.bob,
            project_owner=self.bob)

        ProjectMembership.objects.create(
            project=self.sp,
            user=self.bob,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        self.cf = CoreFunctionProjectFactory.create(
            creator=self.bob,
            program=self.program,
            # data_custodian=self.bob, site_custodian=self.bob,
            project_owner=self.bob)

        ProjectMembership.objects.create(
            project=self.cf,
            user=self.bob,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        self.ext = CollaborationProjectFactory.create(
            creator=self.bob,
            program=self.program,
            # data_custodian=self.bob, site_custodian=self.bob,
            project_owner=self.bob)

        ProjectMembership.objects.create(
            project=self.ext,
            user=self.bob,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

        self.stp = StudentProjectFactory.create(
            creator=self.bob,
            program=self.program,
            # data_custodian=self.bob, site_custodian=self.bob,
            project_owner=self.bob)

        ProjectMembership.objects.create(
            project=self.stp,
            user=self.bob,
            role=ProjectMembership.ROLE_RESEARCH_SCIENTIST)

    def tearDown(self):
        """Destroy test objects after a test."""
        [m.delete for m in ProjectMembership.objects.all()]
        self.sp.delete()
        self.cf.delete()
        self.ext.delete()
        self.stp.delete()
        self.program.delete()
        self.superuser.delete()
        self.bob.delete()
        self.steven.delete()
        self.marge.delete()
        self.peter.delete()

    def test_new_arar(self):
        """Test new ARAR creates updates and changes project status."""
        print("\n  Fast-track {0} to active".format(self.sp.debugname))
        self.assertEqual(self.sp.status, Project.STATUS_NEW)
        self.sp.status = Project.STATUS_ACTIVE
        self.sp.save()
        self.assertEqual(self.sp.status, Project.STATUS_ACTIVE)

        print("  Fast-track {0} to active".format(self.cf.debugname))
        self.assertEqual(self.cf.status, Project.STATUS_NEW)
        self.cf.status = Project.STATUS_ACTIVE
        self.cf.save()
        self.assertEqual(self.cf.status, Project.STATUS_ACTIVE)

        print("  {0} should be active".format(self.ext.debugname))
        self.assertEqual(self.cf.status, Project.STATUS_ACTIVE)

        print("  {0} should be active".format(self.stp.debugname))
        self.assertEqual(self.stp.status, Project.STATUS_ACTIVE)

        print("  Create ARAR")
        self.arar = ARARReport.objects.create(
            year=self.sp.year,
            date_open=datetime.now(),
            date_closed=datetime.now())
        print("  New {0} requests progress reports".format(self.arar.fullname))

        print("  Test saving changed object to db")
        self.sp = self.sp.progressreport.project
        self.sp.save()
        self.cf = self.cf.progressreport.project
        self.cf.save()
        self.stp = self.stp.progressreport.project
        self.stp.save()

        print("  {0} should have a progressreport".format(self.sp.debugname))
        self.assertTrue(self.sp.progressreport is not None)

        print("  {0} should have a progressreport".format(self.cf.debugname))
        self.assertTrue(self.cf.progressreport is not None)

        print("  {0} should have a progressreport".format(self.stp.debugname))
        self.assertTrue(self.stp.progressreport is not None)

        print("  {0} should be updating".format(self.sp.debugname))
        self.assertEqual(self.sp.status, Project.STATUS_UPDATE)

        print("  {0} should be updating".format(self.cf.debugname))
        self.assertEqual(self.cf.status, Project.STATUS_UPDATE)

        print("  {0} should be active".format(self.ext.debugname))
        self.assertEqual(self.ext.status, Project.STATUS_ACTIVE)

        print("  {0} should be updating".format(self.stp.debugname))
        self.assertEqual(self.stp.status, Project.STATUS_UPDATE)
