# -*- coding: utf-8 -*-
"""Filters for Pythia Projects."""
# import rest_framework_filters as filters
import logging
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.db import models as geo_models
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet
from django_filters.filters import (  # noqa
    DateFilter,  # DateTimeFilter,
    BooleanFilter, CharFilter, RangeFilter,
    ChoiceFilter, MultipleChoiceFilter,
    ModelChoiceFilter, ModelMultipleChoiceFilter)
# from shared.filters import FILTER_OVERRIDES
from pythia.projects import models

logger = logging.getLogger(__name__)

class ProjectFilter(FilterSet):
    """Project Filter.

    https://django-filter.readthedocs.io/en/latest/usage.html
    """

    class Meta:
        """Options for ProjectFilter."""
        model = models.Project
        fields = [
            "type",
            "status",
            "year",
            # "program__division",
            "program",   
        ]