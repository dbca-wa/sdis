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

from pythia.models import ()
from pythia.projects.models import ()
from pythia.document.models import ()
from pythia.reports.models import ()

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
