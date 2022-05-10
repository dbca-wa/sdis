from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

import factory
from pythia.models import (Division, Service, Program)
from pythia.documents.models import (
    ConceptPlan, ProjectPlan, ProgressReport, ProjectClosure, StudentReport)
from pythia.projects.models import (
    Project, ScienceProject, CoreFunctionProject, CollaborationProject,
    StudentProject)


@override_settings(
    AUTHENTICATION_BACKENDS=('django.contrib.auth.backends.ModelBackend',),)
class BaseTestCase(TestCase):
    pass


class SuperUserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: "superuser%d" % n)
    email = factory.Sequence(lambda n: "superuser%d@test.com" % n)
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = "Test"
    last_name = "Superuser"
    is_active = True
    is_staff = True
    is_superuser = True


class UserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.Sequence(lambda n: "user%d@test.com" % n)
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = "test"
    last_name = "user"
    is_active = True
    is_staff = True
    is_superuser = False


class ServiceFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Service

    name = factory.Sequence(lambda n: "Division %d" % n)
    slug = factory.Sequence(lambda n: "division%d" % n)
    creator = factory.SubFactory(UserFactory)
    director = factory.SubFactory(UserFactory)


class DivisionFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Division

    name = factory.Sequence(lambda n: "Division %d" % n)
    slug = factory.Sequence(lambda n: "division%d" % n)
    creator = factory.SubFactory(UserFactory)
    director = factory.SubFactory(UserFactory)
    approver = factory.SubFactory(UserFactory)
    

class ProgramFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Program

    name = factory.Sequence(lambda n: "Program %d" % n)
    slug = factory.Sequence(lambda n: "program%d" % n)
    creator = factory.SubFactory(UserFactory)
    division = factory.SubFactory(DivisionFactory)
    position = 10
    program_leader = factory.SubFactory(UserFactory)


class ProjectFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Project

    year = 2017
    number = factory.Sequence(lambda n: n)
    title = "Test Project"
    type = 0
    program = factory.SubFactory(ProgramFactory)
    output_program = factory.SubFactory(ServiceFactory)
    project_owner = factory.SubFactory(UserFactory)
    creator = factory.SubFactory(UserFactory)


class ScienceProjectFactory(ProjectFactory):
    FACTORY_FOR = ScienceProject
    title = "Test Science Project"
    type = 0


class CoreFunctionProjectFactory(ProjectFactory):
    FACTORY_FOR = CoreFunctionProject
    title = "Test Core Function"
    type = 1


class CollaborationProjectFactory(ProjectFactory):
    FACTORY_FOR = CollaborationProject

    title = "Test Collaboration Project"
    type = 2


class StudentProjectFactory(ProjectFactory):
    FACTORY_FOR = StudentProject

    title = "Test Student Project"
    type = 3


class ConceptPlanFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ConceptPlan

    summary = "Test summary"
    outcome = "Test outcome"
    collaborations = "Test collaborations"
    strategic = "Test strategies"


class ProjectPlanFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ProjectPlan

    related_projects = "related projects"
    background = "background"
    aims = "aims"
    outcome = "outcome"
    knowledge_transfer = "knowledge transfer"
    project_tasks = "project"
    references = "references"


class ProgressReportFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ProgressReport

    year = 2014
    context = "context"
    aims = "aims"
    progress = "progress"
    implications = "implications"
    future = "future"


class ProjectClosureFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ProjectClosure

    scientific_outputs = "scientific outputs"
    knowledge_transfer = "knowledge transfer"


class StudentReportFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = StudentReport

    year = 2014
    progress_report = "progress report"
    organisation = "organisation"
