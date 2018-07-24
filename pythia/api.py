"""SDIS API."""

from rest_framework import serializers, viewsets, routers, filters
# from rest_framework.renderers import BrowsableAPIRenderer
# from rest_framework_latex import renderers
# from dynamic_rest import serializers as ds, viewsets as dv
# from django_filters.rest_framework import DjangoFilterBackend
# from drf_extra_fields.geo_fields import PointField
# from rest_framework_gis.serializers import GeoFeatureModelSerializer

# from rest_framework.authentication import (
# SessionAuthentication, BasicAuthentication, TokenAuthentication)

from pythia.models import (
    Program,
    # WebResource, Division,
    Area, User)
from pythia.projects.models import (
    Project,
    # ScienceProject,
    # CoreFunctionProject,
    # CollaborationProject,
    # StudentProject
)
# from pythia.documents.models import (
#     Document,
#     ConceptPlan,
#     ProjectPlan,
#     ProgressReport,
#     ProjectClosure,
#     StudentReport)
# from pythia.reports.models import (ARARReport)


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
                  'area_type',
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
                  'area_type',
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
    type_display = serializers.Field()
    project_type_year_number_plain = serializers.Field()
    team_list_plain = serializers.Field()
    tagline_plain = serializers.Field()
    program = serializers.RelatedField()
    cost_center = serializers.Field()
    status_active = serializers.Field()
    absolute_url = serializers.Field()
    read_only_fields = (
        'id',
        'absolute_url',
        'type',
        'year',
        'number',
        'status_display',
        'type_display',
        'status_active',
        'title_plain',
        'tagline_plain',
        'keywords_plain',
        'cost_center',
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
            'project_type_year_number_plain',
            'title_plain',
            'status_display',
            'status_active',
            'team_list_plain',
            'program',
            'cost_center',
            'start_date',
            'end_date',
            'type',
            'type_display',
            'year',
            'number',
            'tagline_plain',
            'comments',
            'keywords_plain',
            'area_list_nrm_region',
            'area_list_ibra_imcra_region',
            'area_list_dpaw_region',
            'area_list_dpaw_district',
            'absolute_url',
            'image',
        )


class FullProjectSerializer(ProjectSerializer):
    """A comprehensive Project serializer to view project details."""

    status_display = serializers.Field()
    project_type_year_number_plain = serializers.Field()
    team_list_plain = serializers.Field()
    program = ProgramSerializer()
    absolute_url = serializers.Field()
    read_only_fields = (
        'id',
        'absolute_url',
        'type',
        'year',
        'number',
        'status_display',
        'title_plain',
        'tagline_plain',
        'keywords_plain',
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
            'title_plain',
            'tagline_plain',
            'comments',
            'keywords_plain',
            'team_list_plain',
            'program',
            'start_date',
            'end_date',
            'area_list_nrm_region',
            'area_list_ibra_imcra_region',
            'area_list_dpaw_region',
            'area_list_dpaw_district'
        )


# -----------------------------------------------------------------------------#
# Viewsets
class AreaViewSet(viewsets.ModelViewSet):
    """A clever Area ViewSet that returns fast lists and full details.

    The detail page contains a GeoJSON geometry (MultiPolygon) for each area.
    Example: "Avon Wheatbelt" `/api/areas/1/ </api/areas/1/>`_.

    Filter fields: area_type

    Area types
    ----------
    * "Relevant Area Polygon"
      `/api/areas/?area_type=1 </api/areas/?area_type=1>`_
    * "Fieldwork Area Polygon"
      `/api/areas/?area_type=2 </api/areas/?area_type=2>`_
    * "DBCA Region" `/api/areas/?area_type=3 </api/areas/?area_type=3>`_
    * "DBCA District" `/api/areas/?area_type=4 </api/areas/?area_type=4>`_
    * "IBRA" `/api/areas/?area_type=5 </api/areas/?area_type=5>`_
    * "IMCRA" `/api/areas/?area_type=6 </api/areas/?area_type=6>`_
    * "Natural Resource Management Region"
      `/api/areas/?area_type=7 </api/areas/?area_type=7>`_
    """

    queryset = Area.objects.all()
    filter_fields = (
        'area_type',
    )

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
    """A clever Program ViewSet that returns fast lists and full details.

    The detail page provides more fields.
    Example: `/api/programs/5/ </api/programs/5/>`_

    Filter fields: published

    * Published programs:
      `/api/programs/?published=True </api/programs/?published=True>`_
    * Retired or administrative programs:
      `/api/programs/?published=False </api/programs/?published=False>`_
    """

    queryset = Program.objects.all()

    filter_fields = ("published", )

    def get_serializer_class(self):
        """Toggle serializer: Minimal list, full details."""
        if self.action == 'list':
            return ProgramSerializer
        if self.action == 'retrieve':
            return FullProgramSerializer
        return FullProgramSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """A list of publishable projects with more comprehensive detail views.

    Publishable are all approved or successfully completed projects.
    Exempt from this list are new, not yet approved or terminated projects.

    Filter fields: program name, year, number, status, area_list_nrm_region,
    area_list_ibra_imcra_region, area_list_dpaw_region, area_list_dpaw_district

    Program
    * /api/projects/?program__name=Biogeography
    * /api/projects/?program__name=Ecosystem Science

    Year
    * [/api/projects/?year=2016](/api/projects/?year=2016)

    Number
    * [/api/projects/?number=12](/api/projects/?number=12)

    Status
    * [/api/projects/?status=active](/api/projects/?status=active)
    * Status choices: 'active', 'updating', 'closure requested', 'closing',
      'final update', 'completed'.

    Location
    Note: no partial match, e.g.
    /api/projects/?area_list_dpaw_district=Moora only returns projects with
    only Moora, but not projects with Moora and additional districts.

    * /api/projects/?area_list_nrm_region=Rangelands
    * area_list_nrm_region choices: /api/areas/?area_type=7
    * area_list_ibra_imcra_region choices: /api/areas/?area_type=5
      and /api/areas/?area_type=6
    * area_list_dpaw_region choices: /api/areas/?area_type=3
    * area_list_dpaw_district choices: /api/areas/?area_type=4


    Search fields
    Fulltext search with partial, case-insensitive match works on
    title, tagline, keywords, and all four area fields.

    * All projects with "adaptive" in title or tagline:
      /api/projects/?search=adaptive
    * All projects in (at least) DBCA District Moora:
      /api/projects/?search=Moora
    """

    queryset = Project.published.all()
    filter_backends = (filters.SearchFilter,)
    filter_fields = (
        'status',
        'year',
        'number',
        'type',
        'status_active',
        'cost_center',
        'area_list_nrm_region',
        'area_list_ibra_imcra_region',
        'area_list_dpaw_region',
        'area_list_dpaw_district',
    )
    search_fields = (
        'title',
        'program__name',
        'tagline',
        'keywords_plain',
        'area_list_nrm_region',
        'area_list_ibra_imcra_region',
        'area_list_dpaw_region',
        'area_list_dpaw_district',
    )

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
router.register(r'projects', ProjectViewSet, base_name="projects")
