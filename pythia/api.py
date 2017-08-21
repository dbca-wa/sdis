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
    """A User serializer."""

    class Meta:
        """Class opts."""

        model = User
        fields = ('username', 'email', 'is_staff')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    """A minimal Project serializer to build a filterable list."""

    project_type_year_number_plain = serializers.Field()
    title_plain = serializers.Field()
    tagline_plain = serializers.Field()
    comments_plain = serializers.Field()
    team_list_plain = serializers.Field()
    read_only_fields = ('type', 'year', 'number', 'status', 'team_list_plain')

    class Meta:
        """Class opts."""

        model = Project
        fields = (
            'id',
            'project_type_year_number_plain',
            'title_plain',
            'status',
            'tagline_plain',
            'comments_plain',
            'image',
            'team_list_plain',
            )


class FullProjectSerializer(ProjectSerializer):
    """A comprehensive Project serializer to view project details."""

    project_type_year_number_plain = serializers.Field()
    team_list_plain = serializers.Field()
    area_nrm_region = serializers.Field()
    area_dpaw_region = serializers.Field()
    area_dpaw_district = serializers.Field()
    area_ibra_imcra_region = serializers.Field()
    read_only_fields = ('type', 'year', 'number', 'status',)

    class Meta:
        """Class opts."""

        model = Project
        fields = (
            'id',
            'type',
            'year',
            'number',
            'status',
            'project_type_year_number_plain',
            'title_plain',
            'team_list_plain',
            'area_nrm_region',
            'area_ibra_imcra_region',
            'area_dpaw_region',
            'area_dpaw_district',
            )


# -----------------------------------------------------------------------------#
# Viewsets
class UserViewSet(viewsets.ModelViewSet):
    """A default User ViewSet."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """A clever Project ViewSet that returns fast lists and full details."""

    queryset = Project.objects.all()

    def get_serializer_class(self):
        """Toggle serializer: Minimal list, full details."""
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
