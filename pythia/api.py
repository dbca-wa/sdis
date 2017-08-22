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
class AreaSerializer(serializers.HyperlinkedModelSerializer):
    """A simple Area serializer."""

    area_type_display = serializers.Field()

    read_only_fields = (
        'area_type_display',
        'northern_extent',)

    class Meta:
        """Class opts."""

        model = Area
        fields = ('id',
                  'name',
                  'area_type_display',
                  'northern_extent')


class FullAreaSerializer(serializers.HyperlinkedModelSerializer):
    """A comprehensive Area serializer."""

    area_type_display = serializers.Field()

    read_only_fields = (
        'area_type_display',
        'northern_extent',)

    class Meta:
        """Class opts."""

        model = Area
        fields = ('id',
                  'name',
                  'area_type_display',
                  'northern_extent',
                  'mpoly')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """A User serializer."""

    fullname = serializers.Field()

    class Meta:
        """Class opts."""

        model = User
        fields = ('id',
                  'fullname',
                  'username',
                  'email',
                  'is_staff')


class ProgramSerializer(serializers.HyperlinkedModelSerializer):
    """A fast and simple Program serializer."""

    program_leader = serializers.RelatedField()

    class Meta:
        """Class opts."""

        model = Program
        fields = (
            'id',
            'name',
            'slug',
            'published',
            'position',
            'cost_center',
            'image',
            'program_leader',
            )


class FullProgramSerializer(serializers.HyperlinkedModelSerializer):
    """A comprehensive Program serializer."""
    program_leader = UserSerializer()
    finance_admin = UserSerializer()
    data_custodian = UserSerializer()

    class Meta:
        """Class opts."""

        model = Program
        fields = (
            'id',
            'name',
            'slug',
            'published',
            'position',
            'cost_center',
            'focus',
            'introduction',
            'image',
            'program_leader',
            'finance_admin',
            'data_custodian')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    """A minimal Project serializer to build a filterable list."""

    status_display = serializers.Field()
    project_type_year_number_plain = serializers.Field()
    title_plain = serializers.Field()
    tagline_plain = serializers.Field()
    team_list_plain = serializers.Field
    program = serializers.RelatedField()
    absolute_url = serializers.Field()
    read_only_fields = (
        'type',
        'year',
        'number',
        'status_display',
        'team_list_plain',
        'program',
        'absolute_url',
        )

    class Meta:
        """Class opts."""

        model = Project
        fields = (
            'id',
            'absolute_url',
            'project_type_year_number_plain',
            'title_plain',
            'status_display',
            'tagline_plain',
            'comments',
            'image',
            'team_list_plain',
            'program',
            'area_list_nrm_region',
            'area_list_ibra_imcra_region',
            'area_list_dpaw_region',
            'area_list_dpaw_district',
            )


class FullProjectSerializer(ProjectSerializer):
    """A comprehensive Project serializer to view project details."""

    status_display = serializers.Field()
    project_type_year_number_plain = serializers.Field()
    team_list_plain = serializers.Field()
    program = FullProgramSerializer()
    absolute_url = serializers.Field()
    read_only_fields = (
        'id',
        'absolute_url',
        'type',
        'year',
        'number',
        'status',
        'title_plain',
        'tagline_plain',
        'program',
        'area_list_nrm_region',
        'area_list_ibra_imcra_region',
        'area_list_dpaw_region',
        'area_list_dpaw_district',
        )

    class Meta:
        """Class opts."""

        model = Project
        fields = (
            'id',
            'absolute_url',
            'type',
            'year',
            'number',
            'status_display',
            'project_type_year_number_plain',
            'title',
            'title_plain',
            'tagline_plain',
            'comments',
            'team_list_plain',
            'program',
            'area_nrm_region',
            'area_ibra_imcra_region',
            'area_dpaw_region',
            'area_dpaw_district',
            )


# -----------------------------------------------------------------------------#
# Viewsets
class AreaViewSet(viewsets.ModelViewSet):
    """A clever Area ViewSet that returns fast lists and full details."""

    queryset = Area.objects.all()

    def get_serializer_class(self):
        """Toggle serializer: Minimal list, full details."""
        if self.action == 'list':
            return AreaSerializer
        if self.action == 'retrieve':
            return FullAreaSerializer
        return FullAreaSerializer


class UserViewSet(viewsets.ModelViewSet):
    """A default User ViewSet."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    """A clever Program ViewSet that returns fast lists and full details."""

    queryset = Program.objects.all()

    def get_serializer_class(self):
        """Toggle serializer: Minimal list, full details."""
        if self.action == 'list':
            return ProgramSerializer
        if self.action == 'retrieve':
            return FullProgramSerializer
        return FullProgramSerializer


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
router.register(r'areas', AreaViewSet)
router.register(r'users', UserViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'projects', ProjectViewSet)
