from rest_framework import serializers, viewsets, routers
# from rest_framework.renderers import BrowsableAPIRenderer
# from rest_framework_latex import renderers
# import rest_framework_filters as filters
# from dynamic_rest import serializers as ds, viewsets as dv
# from django_filters.rest_framework import DjangoFilterBackend
# from drf_extra_fields.geo_fields import PointField
# from rest_framework_gis.serializers import GeoFeatureModelSerializer

from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication, TokenAuthentication)

from pythia.models import Program, WebResource, Division, Area, User
from pythia.projects.models import (
    Project, ScienceProject, CoreFunctionProject, CollaborationProject,
    StudentProject)
from pythia.documents.models import (
    Document, ConceptPlan, ProjectPlan, ProgressReport, ProjectClosure,
    StudentReport)
from pythia.reports.models import (ARARReport)


# -----------------------------------------------------------------------------#
# Serializers
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'is_staff')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'type', 'year', 'number', 'status',
                  'title', 'tagline', 'image')


# -----------------------------------------------------------------------------#
# Viewsets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

# -----------------------------------------------------------------------------#
# Routers
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
