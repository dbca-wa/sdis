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
    title_plain = serializers.Field()
    tagline_plain = serializers.Field()
    comments_plain = serializers.Field()
    read_only_fields = ('type', 'year', 'number', 'status',)

    class Meta:
        model = Project
        fields = ('id', 'type', 'year', 'number', 'status',
                  'title_plain', 'tagline_plain', 'comments_plain', 'image')


class FullProjectSerializer(ProjectSerializer):
    area_nrm_region = serializers.Field()
    area_dpaw_region = serializers.Field()
    area_dpaw_district = serializers.Field()
    area_ibra_imcra_region = serializers.Field()
    read_only_fields = ('type', 'year', 'number', 'status',)

    class Meta:
        model = Project
        fields = ('id', 'type', 'year', 'number', 'status',
                  'area_nrm_region',  'area_ibra_imcra_region',
                  'area_dpaw_region', 'area_dpaw_district',
                  )


# -----------------------------------------------------------------------------#
# Viewsets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectSerializer
        if self.action == 'retrieve':
            return FullProjectSerializer
        return FullProjectSerializer


# -----------------------------------------------------------------------------#
# Routers
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
