# -*- coding: utf-8 -*-
"""Filters for Pythia Projects."""
# import rest_framework_filters as filters
import logging
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.db import models as geo_models
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, DateRangeFilter, CharFilter, ChoiceFilter, MultipleChoiceFilter
# from django_filters.filters import (  # noqa
#     DateFilter,  # DateTimeFilter,
#     BooleanFilter, CharFilter, RangeFilter,
#     ChoiceFilter, MultipleChoiceFilter,
#     ModelChoiceFilter, ModelMultipleChoiceFilter)
# from shared.filters import FILTER_OVERRIDES

from collections import OrderedDict  # noqa
from dateutil.relativedelta import relativedelta

from django.contrib.gis.db import models as geo_models
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from leaflet.forms.widgets import LeafletWidget

from pythia.projects.models import Project

logger = logging.getLogger(__name__)


# Fix collapsing widget width
# https://github.com/applegrew/django-select2/issues/252
S2ATTRS = {'data-width': '50em'}

LEAFLET_WIDGET_ATTRS = {
    'map_height': '700px',
    'map_width': '100%',
    'display_raw': 'true',
    'map_srid': 4326,
}
LEAFLET_SETTINGS = {'widget': LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)}

_truncate = lambda dt: dt.replace(hour=0, minute=0, second=0)

class CustomDateRangeFilter(DateRangeFilter):
    """A django-filters DateRangeFilter with useful presets."""
    options = {
        '': (_('Any date'), lambda qs, name: qs.all()),
        1: (_('This year'), lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
        })),
        2: (_('Past year'), lambda qs, name: qs.filter(**{
            '%s__gte' % name: _truncate(now() - relativedelta(months=12)),
            '%s__lt' % name: _truncate(now() + relativedelta(days=1)),
        })),
        3: (_('Past six months'), lambda qs, name: qs.filter(**{
            '%s__gte' % name: _truncate(now() - relativedelta(months=6)),
            '%s__lt' % name: _truncate(now() + relativedelta(days=1)),
        })),
        4: (_('Past three months'), lambda qs, name: qs.filter(**{
            '%s__gte' % name: _truncate(now() - relativedelta(months=3)),
            '%s__lt' % name: _truncate(now() + relativedelta(days=1)),
        })),
        # 4: (_('This month'), lambda qs, name: qs.filter(**{
        #     '%s__year' % name: now().year,
        #     '%s__month' % name: now().month
        # })),
        # 5: (_('Yesterday'), lambda qs, name: qs.filter(**{
        #     '%s__year' % name: now().year,
        #     '%s__month' % name: now().month,
        #     '%s__day' % name: (now() - relativedelta(days=1)).day,
        # })),
        # 6: (_('Today'), lambda qs, name: qs.filter(**{
        #     '%s__year' % name: now().year,
        #     '%s__month' % name: now().month,
        #     '%s__day' % name: now().day
        # })),
    }


class CustomDateTimeRangeFilter(DateRangeFilter):
    """A django-filters DateTimeRangeFilter with useful presets."""
    
    options = {
        '': (_('Any date'), lambda qs, name: qs.all()),
        # 1: (_('Today'), lambda qs, name: qs.filter(**{
        #     '%s__year' % name: now().year,
        #     '%s__month' % name: now().month,
        #     '%s__day' % name: now().day
        # })),
        4: (_('This year'), lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
        })),
        2: (_('Past year'), lambda qs, name: qs.filter(**{
            '%s__gte' % name: _truncate(now() - relativedelta(months=12)),
            '%s__lt' % name: _truncate(now() + relativedelta(days=1)),
        })),

        2: (_('Past six months'), lambda qs, name: qs.filter(**{
            '%s__gte' % name: _truncate(now() - relativedelta(months=6)),
            '%s__lt' % name: _truncate(now() + relativedelta(days=1)),
        })),
        # 3: (_('This month'), lambda qs, name: qs.filter(**{
        #     '%s__year' % name: now().year,
        #     '%s__month' % name: now().month
        # })),
        # 5: (_('Yesterday'), lambda qs, name: qs.filter(**{
        #     '%s__year' % name: now().year,
        #     '%s__month' % name: now().month,
        #     '%s__day' % name: (now() - relativedelta(days=1)).day,
        # })),
    }


FILTER_OVERRIDES = {
    models.CharField: {
        'filter_class': CharFilter,
        'extra': lambda f: {'lookup_expr': 'icontains', },
    },
    models.TextField: {
        'filter_class': CharFilter,
        'extra': lambda f: {'lookup_expr': 'icontains', },
    },
    models.DateField: {
        'filter_class': CustomDateRangeFilter,
    },
    models.DateTimeField: {
        'filter_class': CustomDateTimeRangeFilter,
    },
    geo_models.PointField: {
        'filter_class': CharFilter,
        'extra': lambda f: {
            'lookup_expr': 'intersects',
            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)
        },
    },
    geo_models.LineStringField: {
        'filter_class': CharFilter,
        'extra': lambda f: {
            'lookup_expr': 'intersects',
            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)
        },
    },
    geo_models.MultiLineStringField: {
        'filter_class': CharFilter,
        'extra': lambda f: {
            'lookup_expr': 'intersects',
            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)
        },
    },
    geo_models.PolygonField: {
        'filter_class': CharFilter,
        'extra': lambda f: {
            'lookup_expr': 'intersects',
            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)
        },
    },
    geo_models.MultiPolygonField: {
        'filter_class': CharFilter,
        'extra': lambda f: {
            'lookup_expr': 'intersects',
            'widget': LeafletWidget(attrs=LEAFLET_SETTINGS)
        },
    }
}


class ProjectFilter(FilterSet):
    """Project Filter.

    https://django-filter.readthedocs.io/en/latest/usage.html
    """

    title = CharFilter(lookup_type="icontains")
    type = MultipleChoiceFilter(choices = Project.PROJECT_TYPES)
    status = MultipleChoiceFilter(choices = Project.STATUS_CHOICES)
    start_date = CustomDateRangeFilter()

    class Meta:
        """Options for ProjectFilter."""
        model = Project
        filter_overrides = FILTER_OVERRIDES
        fields = [
            "title",
            "type",
            "status",
            "year",
            "number",
            "program__division",
            "program__published",
            "program",
            "start_date",
        ]