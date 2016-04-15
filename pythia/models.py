from __future__ import (division, print_function, unicode_literals,
absolute_import)
import reversion
import threading
import logging


from django.conf import settings
from django.core import validators
from django.db.models import signals
from django.core.mail import send_mail
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager, Group)
from django.contrib.auth import get_user_model

from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

import logging
from smart_selects.db_fields import ChainedForeignKey

#from swingers.models import Audit, ActiveModel
from django.contrib.gis.db import models

from pythia.fields import Html2TextField

from south.modelsinspector import add_introspection_rules
#add_introspection_rules([], ["^myapp\.stuff\.fields\.SomeNewField"])

logger = logging.getLogger(__name__)


#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

# we can't do `from swingers import models` because that causes circular import
#from swingers.models import Model, ForeignKey, DateTimeField

from django.contrib.gis.db import models as geo_models
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone, six
from django.db import router, models
from django.db.models import signals
from django.db.models.deletion import Collector


#from swingers.models.managers import ActiveModelManager, ActiveGeoModelManager
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.sql.query import Query

from django.contrib.gis.db import models as geo_models
from django.contrib.gis.db.models.query import GeoQuerySet
from django.contrib.gis.db.models.sql.query import GeoQuery

import copy

logger = logging.getLogger("log." + __name__)

_locals = threading.local()


def get_locals():
    """
    Setup locals for a request thread so we can attach stuff and make it
    available globally.
    import from request.models::
        from request.models import get_locals
        _locals = get_locals
        _locals.request.user = amazing
    """
    return _locals


class ActiveQuerySet(QuerySet):
    def __init__(self, model, query=None, using=None):
        # the model needs to be defined so that we can construct our custom
        # query
        if query is None:
            query = Query(model)
            query.add_q(models.Q(effective_to__isnull=True))
        return super(ActiveQuerySet, self).__init__(model, query, using)

    def __deepcopy__(self, memo):
        # borrowed from django.db.models.query.QuerySet because we need to pass
        # self.model to the self.__class__ call
        obj = self.__class__(self.model)
        for k, v in self.__dict__.items():
            if k in ('_iter', '_result_cache'):
                obj.__dict__[k] = None
            else:
                obj.__dict__[k] = copy.deepcopy(v, memo)
                return obj

    def delete(self):
        # see django.db.models.query.QuerySet.delete
        assert_msg = "Cannot use 'limit' or 'offset' with delete."
        assert self.query.can_filter(), assert_msg

        del_query = self._clone()
        del_query._for_write = True

        # Disable non-supported fields.
        del_query.query.select_for_update = False
        del_query.query.select_related = False
        del_query.query.clear_ordering(force_empty=True)

        # TODO: this could probably be made more efficient via the django
        # Collector, maybe
        for obj in del_query:
            obj.delete()

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None
    delete.alters_data = True


class ActiveGeoQuerySet(ActiveQuerySet, GeoQuerySet):
    def __init__(self, model, query=None, using=None):
        # the model needs to be defined so that we can construct our custom
        # query
        if query is None:
            query = GeoQuery(model)
            query.add_q(geo_models.Q(effective_to__isnull=True))
        return super(ActiveGeoQuerySet, self).__init__(model, query, using)


class ActiveModelManager(models.Manager):
    '''Exclude inactive ("deleted") objects from the query set.'''
    def get_query_set(self):
        '''Override the default queryset to filter out deleted objects.
        '''
        return ActiveQuerySet(self.model)

    # __getattr__ borrowed from
    # http://lincolnloop.com/django-best-practices/applications.html#managers
    def __getattr__(self, attr, *args):
        # see https://code.djangoproject.com/ticket/15062 for
        # details
        if attr.startswith("_"):
            raise AttributeError
        return getattr(self.get_query_set(), attr, *args)


class ActiveGeoModelManager(ActiveModelManager, geo_models.GeoManager):
    def get_query_set(self):
        return ActiveGeoQuerySet(self.model)


class ActiveModel(models.Model):
    '''
    Model mixin to allow objects to be saved as 'non-current' or 'inactive',
    instead of deleting those objects.
    The standard model delete() method is overridden.

    "effective_from" allows 'past' and/or 'future' objects to be saved.
    "effective_to" is used to 'delete' objects (null==not deleted).
    '''
    effective_from = models.DateTimeField(default=timezone.now)
    effective_to = models.DateTimeField(null=True, blank=True)
    objects = ActiveModelManager()
    # Return all objects, including deleted ones, the default manager.
    objects_all = models.Manager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        if not issubclass(type(type(self).objects), ActiveModelManager):
            raise ImproperlyConfigured(
                "The ActiveModel objects manager is not a subclass of "
                "swingers.base.models.managers.ActiveModelManager, if you "
                "created your own objects manager, it must be a subclass of "
                "ActiveModelManager.")
        super(ActiveModel, self).__init__(*args, **kwargs)

    def is_active(self):
        return self.effective_to is None

    def is_deleted(self):
        return not self.is_active()

    def delete(self, *args, **kwargs):
        '''
        Overides the standard model delete method; sets "effective_to" as the
        current date and time and then calls save() instead.
        '''
        # see django.db.models.deletion.Collection.delete
        using = kwargs.get('using', router.db_for_write(self.__class__,
                                                        instance=self))
        cannot_be_deleted_assert = ("""%s object can't be deleted because its
                                    %s attribute is set to None.""" %
                                    (self._meta.object_name,
                                     self._meta.pk.attname))
        assert self._get_pk_val() is not None, cannot_be_deleted_assert
        collector = Collector(using=using)
        collector.collect([self])
        collector.sort()

        # send pre_delete signals
        def delete(collector):
            for model, obj in collector.instances_with_model():
                if not model._meta.auto_created:
                    signals.pre_delete.send(
                        sender=model, instance=obj, using=using
                    )

            # be compatible with django 1.4.x
            if hasattr(collector, 'fast_deletes'):
                # fast deletes
                for qs in collector.fast_deletes:
                    for instance in qs:
                        self._delete(instance)

            # delete batches
            # be compatible with django>=1.6
            if hasattr(collector, 'batches'):
                for model, batches in six.iteritems(collector.batches):
                    for field, instances in six.iteritems(batches):
                        for instance in instances:
                            self._delete(instance)

            # "delete" instances
            for model, instances in six.iteritems(collector.data):
                for instance in instances:
                    self._delete(instance)

            # send post_delete signals
            for model, obj in collector.instances_with_model():
                if not model._meta.auto_created:
                    signals.post_delete.send(
                        sender=model, instance=obj, using=using
                    )

        # another django>=1.6 thing
        try:
            from django.db.transaction import commit_on_success_unless_managed
        except ImportError:
            delete(collector)
        else:
            commit_on_success_unless_managed(using=using)(delete(collector))

    delete.alters_data = True

    def _delete(self, instance):
        instance.effective_to = timezone.now()
        instance.save()


class ActiveGeoModel(ActiveModel):
    objects = ActiveGeoModelManager()
    # Return all objects, including deleted ones, the default manager.
    objects_all = geo_models.GeoManager()

    def __init__(self, *args, **kwargs):
        if not issubclass(type(type(self).objects), ActiveGeoModelManager):
            raise ImproperlyConfigured(
                "The ActiveGeoModel objects manager is not a subclass of "
                "swingers.base.models.models.ActiveGeoModelManager, if you "
                "created your own objects manager, it must be a subclass of "
                "ActiveGeoModelManager.")
        super(ActiveGeoModel, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True

@python_2_unicode_compatible
class Audit(geo_models.Model):
    class Meta:
        abstract = True

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(app_label)s_%(class)s_created',
        editable=False)
    modifier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(app_label)s_%(class)s_modified',
        editable=False)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __init__(self, *args, **kwargs):
        super(Audit, self).__init__(*args, **kwargs)
        self._changed_data = None
        self._initial = {}
        if self.pk:
            for field in self._meta.fields:
                self._initial[field.attname] = getattr(self, field.attname)

    def has_changed(self):
        """
        Returns true if the current data differs from initial.
        """
        return bool(self.changed_data)

    def _get_changed_data(self):
        if self._changed_data is None:
            self._changed_data = []
            for field, value in self._initial.items():
                if field in ["modified", "modifier_id"]:
                    continue
                if getattr(self, field) != value:
                    self._changed_data.append(field)
        return self._changed_data
    changed_data = property(_get_changed_data)

    def save(self, *args, **kwargs):
        """
        This falls back on using an admin user if a thread request object
        wasn't found.
        """
        if ((not hasattr(_locals, "request") or
             _locals.request.user.is_anonymous())):
            if hasattr(_locals, "user"):
                user = _locals.user
            else:
                user = User.objects.get(id=1)
                _locals.user = user
        else:
            user = _locals.request.user

        # If saving a new model, set the creator.
        if not self.pk:
            self.creator = user
            created = True
        else:
            created = False

        self.modifier = user
        super(Audit, self).save(*args, **kwargs)

        if created:
            with reversion.create_revision():
                reversion.set_comment('Initial version.')
        else:
            if self.has_changed():
                comment = 'Changed ' + ', '.join(self.changed_data) + '.'
                with reversion.create_revision():
                    reversion.set_comment(comment)
            else:
                with reversion.create_revision():
                    reversion.set_comment('Nothing changed.')

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        opts = self._meta.app_label, self._meta.module_name
        return reverse("admin:%s_%s_change" % opts, args=(self.pk, ))

    def clean_fields(self, exclude=None):
        """
        Override clean_fields to do what model validation should have done
        in the first place -- call clean_FIELD during model validation.
        """
        errors = {}

        for f in self._meta.fields:
            if f.name in exclude:
                continue
            if hasattr(self, "clean_%s" % f.attname):
                try:
                    getattr(self, "clean_%s" % f.attname)()
                except ValidationError as e:
                    # TODO: Django 1.6 introduces new features to
                    # ValidationError class, update it to use e.error_list
                    errors[f.name] = e.messages

        try:
            super(Audit, self).clean_fields(exclude)
        except ValidationError as e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)
# end swingers models
#-----------------------------------------------------------------------------#
# Report Parts
#
class ReportPart(object):
    def __str__(self):
        return str(self.original)

    def __init__(self, original, template, context, *args):
        self.original = original
        self.template_ = template
        self.context_ = context

    @property
    def template(self):
        return self.base + self.template_ + self.suffix

    @property
    def context(self):
        if callable(self.context_):
            context_ = self.context_(self.original)
        elif hasattr(self.original, self.context_):
            context_ = getattr(self.original, self.context_)
        else:
            context_ = self.context_
        return context_


class HTMLReportPart(ReportPart):
    suffix = '.html'
    base = 'admin/pythia/ararreport/includes/'


class LATEXReportPart(ReportPart):
    suffix = '.tex'
    base = 'latex/includes/'


#-----------------------------------------------------------------------------#
# Shared classes: Administrative departmental structures
#
@python_2_unicode_compatible
class Area(Audit):  # , models.PolygonModelMixin):
    """
    An area of interest to a Project, classified by area type.
    """
    AREA_TYPE_RELEVANT = 1
    AREA_TYPE_FIELDWORK = 2
    AREA_TYPE_DPAW_REGION = 3
    AREA_TYPE_DPAW_DISTRICT = 4
    AREA_TYPE_IBRA_REGION = 5
    AREA_TYPE_IMCRA_REGION = 6
    AREA_TYPE_NRM_REGION = 7
    AREA_TYPE_CHOICES = (
        (AREA_TYPE_RELEVANT,  _("Relevant Area Polygon")),
        (AREA_TYPE_FIELDWORK, _("Fieldwork Area Polygon")),
        (AREA_TYPE_DPAW_REGION, _("DPaW Region")),
        (AREA_TYPE_DPAW_DISTRICT, _("DPaW District")),
        (AREA_TYPE_IBRA_REGION, _("IBRA")),
        (AREA_TYPE_IMCRA_REGION, _("IMCRA")),
        (AREA_TYPE_NRM_REGION, _("Natural Resource Management Region"))
    )
    area_type = models.PositiveSmallIntegerField(
        verbose_name=_("Area Type"), choices=AREA_TYPE_CHOICES,
        default=AREA_TYPE_RELEVANT)
    name = models.CharField(
        max_length=320, null=True, blank=True,
        help_text=_("A human-readable, short but descriptive name."))
    source_id = models.PositiveIntegerField(
        null=True, blank=True,
        help_text=_("The source id"))
    northern_extent = models.FloatField(
        null=True, blank=True,
        help_text=_("The maximum northern extent of an Area, "
                    "useful for sorting by geographic latitude."))
    mpoly = geo_models.MultiPolygonField(
        blank=True, null=True, srid=4326, verbose_name=_("Spatial extent"),
        help_text=_("The spatial extent of this feature, stored as WKT."))

    class Meta:
        verbose_name = _("area")
        verbose_name_plural = _("areas")
        ordering = ['area_type','-northern_extent']

    def save(self, *args, **kwargs):
	if self.get_northern_extent() is not None:
            self.northern_extent = self.get_northern_extent()
        super(Area, self).save(*args, **kwargs)

    def __str__(self):
        return '[{0}] {1}'.format(self.get_area_type_display(), self.name)

    def get_northern_extent(self):
        return self.mpoly.extent[3] if self.mpoly else None

class RegionManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


@python_2_unicode_compatible
class Region(models.Model):
    """
    DPaW Region
    """
    mpoly = geo_models.MultiPolygonField(
        null=True, blank=True, help_text='Optional cache of spatial features.')
    # the name should be unique=True
    name = models.CharField(max_length=64, null=True, blank=True)
    northern_extent = models.FloatField(null=True, blank=True)
    objects = RegionManager()

    class Meta:
        verbose_name = _("region")
        verbose_name_plural = _("regions")
        ordering = ['-northern_extent']

    def __str__(self):
        return self.name if self.name else str(self.pk)

    def save(self, *args, **kw):
        self.northern_extent = self.get_northern_extent()
        super(Region, self).save(*args, **kw)

    def natural_key(self):
        return (self.name,)

    def get_northern_extent(self):
        return self.mpoly.extent[3] if self.mpoly else 0


class DistrictManager(models.Manager):
    def get_by_natural_key(self, region, name):
        region = Region.objects.get_by_natural_key(region)
        return self.get(name=name, region=region)


@python_2_unicode_compatible
class District(models.Model):
    """
    DPaW District
    """
    # the name should be unique=True
    name = models.CharField(max_length=200, null=True, blank=True)
    code = models.CharField(max_length=3, null=True, blank=True)
    northern_extent = models.FloatField(null=True, blank=True)
    objects = DistrictManager()
    region = models.ForeignKey(
    #ChainedForeignKey(
        Region,
    #    chained_field="name", chained_model_field="name",
    #    show_all=False, auto_choose=True,
        help_text=_("The region to which this district belongs."))
    mpoly = geo_models.MultiPolygonField(
        null=True, blank=True,
        help_text=_("Optional cache of spatial features."))

    def __str__(self):
        return '[{0}] {1}'.format(self.region.name, self.name)

    def save(self, *args, **kw):
        self.northern_extent = self.get_northern_extent()
        super(District, self).save(*args, **kw)

    def natural_key(self):
        return self.region.natural_key() + (self.name,)
    natural_key.dependencies = ['project.region']

    class Meta:
        ordering = ['-northern_extent']
        verbose_name = _("district")
        verbose_name_plural = _("districts")

    def get_northern_extent(self):
        return self.mpoly.extent[3] if self.mpoly else 0


@python_2_unicode_compatible
class Address(Audit, ActiveModel):
    """
    An address with street 1, street 2, city, and zip code.
    """
    street = models.CharField(
        max_length=254, help_text=_("The street address"))
    extra = models.CharField(
        _("extra"), max_length=254, null=True, blank=True,
        help_text=_("Additional address info"))
    city = models.CharField(
        max_length=254, help_text=_("The city"))
    zipcode = models.CharField(
        max_length=4, help_text=_("The zip code"))
    state = models.CharField(
        max_length=254, default="WA", help_text=_("The state"))
    country = models.CharField(
        max_length=254, default="Australia", help_text=_("The country"))

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")

    def __str__(self):
        if self.extra:
            return '{0}, {1}, {2} {3} {4}'.format(
                self.street, self.extra, self.city, self.zipcode, self.state)
        else:
            return '{0}, {1} {2} {3}'.format(
                self.street, self.city, self.zipcode, self.state)


@python_2_unicode_compatible
class Division(Audit, ActiveModel):
    """
    Departmental divisions. Divisions are structured into programs.
    The work of Science and Conservation Division is a service provided
    to output programs like Parks and Visitor Services, Nature Cons,
    Sustainable Forest Management and potentially other Divisions.
    """
    name = models.CharField(max_length=320)
    slug = models.SlugField(help_text=_("The acronym of the name."))
    # Key personnel ----------------------------------------------------------#
    director = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='leads_divisions',
        blank=True, null=True, help_text=_("The Division's Director"))

    class Meta:
        verbose_name = _("Departmental Service")
        verbose_name_plural = _("Departmental Services")
        ordering = ['slug','name']



    def __str__(self):
        return 'Service {0}: {1}'.format(self.slug, self.name)


@python_2_unicode_compatible
class Program(Audit, ActiveModel):
    """
    A Science and Conservation Division Program is an organizational
    structure of research scientists, technical officers and admin staff
    such as a dedicated finance admin or a default data custodian
    under the responsibility of a program leader.
    A program has a cost center code which is unique across the Department.
    """
    name = models.CharField(max_length=320)
    slug = models.SlugField(
        help_text='A unique slug to be used in folder names etc.')

    # Publishing and printing options ----------------------------------------#
    published = models.BooleanField(
        default=True,
        verbose_name="Publish this Program?")
    position = models.IntegerField(
        help_text='An arbitrary, ascending ordering number.')

    # Key personnel ----------------------------------------------------------#
    program_leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='leads_programs',
        blank=True, null=True,
        help_text='The Program Leader')
    # cost_center should be unique=True
    cost_center = models.CharField(
        max_length=3, blank=True, null=True,
        help_text='The three-digit cost center number for the Program.')
    finance_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='finance_admin_on_programs',
        help_text='The finance admin.')
    data_custodian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='pythia_data_custodian_on_programs',  # clashes with sdis2
        help_text='The default custodian of data sets of this Program.')

    # About ------------------------------------------------------------------#
    focus = Html2TextField(
        verbose_name='Program focus',
        blank=True, null=True,
        help_text="The program's focus as a semicolon-separated list of "
        "key words.")
    introduction = Html2TextField(
        verbose_name='Program introduction',
        blank=True, null=True,
        help_text="The program's mission in about 150 to 300 words.")

    class Meta:
        ordering = ['position', 'cost_center']

    def __str__(self):
        #return '[{0}-{1}] {2}'.format(self.cost_center, self.slug, self.name)
        return self.name

    def save(self, *args, **kw):
        '''Generate slug from name if not set.'''
        if not self.slug:
            self.slug = slugify(self.name)
        super(Program, self).save(*args, **kw)

    def parts(self, part_class):
        # TODO: we probably only want projects that are on the current ARAR
        # here
        # TODO: :) iterators?

        # self.project_set.all() should not hit the db as it is prefetched from
        # pythia.models.report.programs()
        # get all the crap from the db in a couple of queries, let python
        # crunch the data up :)
        Project = self.project_set.model
        projects = self.project_set.filter(
            type__in=[Project.SCIENCE_PROJECT,
                      Project.CORE_PROJECT]).prefetch_related(
                          'progressreport',
                      )

        return [part_class(project, 'project', lambda x: x)
                for project in projects]

    @property
    def latexparts(self):
        return self.parts(LATEXReportPart)

    @property
    def htmlparts(self):
        return self.parts(HTMLReportPart)

    @property
    def opts(self):
        return self._meta

    @property
    def projects(self):
        Project = self.project_set.model
        #return Project.objects.filter(program=self
        #    ).filter(Q(instance_of='pythia.projects.models.ScienceProject') |
        #            Q(instance_of='pythia.projects.models.CoreFunctionProject')
        #    ).prefetch_related('documents')
        return self.project_set.filter(type__in=[Project.SCIENCE_PROJECT,
            Project.CORE_PROJECT]).prefetch_related('documents')

def set_smt_to_pl(sender, instance, created, **kwargs):
    """Add all Program Leaders to Group SMT.
    If clobber==True, drop all SMT members beforehand.
    """
    smt, created = Group.objects.get_or_create(name='SMT')
    if kwargs.has_key("clobber") and kwargs["clobber"]:
        dropped = [smt.user_set.remove(x) for x in smt.user_set.all()]
        logger.info("Removed all {0} current SMT members.".format(len(dropped)))
    added = [smt.user_set.add(x.program_leader) for x in Program.objects.all()]
    logger.info("Added all {0} current Program Leaders to SMT.".format(len(added)))

# By default, let a Program add its program leader to SMT without removing others
# from it
signals.post_save.connect(set_smt_to_pl, sender=Program)


@python_2_unicode_compatible
class WorkCenter(Audit, ActiveModel):
    """
    A departmental work center is where staff offices are located.
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField()

    # Location ---------------------------------------------------------------#
    physical_address = models.ForeignKey(
        Address, related_name='workcenter_physical_address')
    postal_address = models.ForeignKey(
        Address, related_name='workcenter_postal_address')
    district = models.ForeignKey(District, blank=True, null=True)

    class Meta:
        app_label = 'pythia'
        verbose_name = _("work centre")
        verbose_name_plural = _("work centres")

    def __str__(self):
        return self.name

    def save(self, *args, **kw):
        """
        Generate slug from name if not set.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super(WorkCenter, self).save(*args, **kw)


class WebResourceDomain(Audit, ActiveModel):
    """
    The domain of a Web Resource.
    E.g., social networks like Google Scholar, LinkedIn, ResearchGate et al.
    """
    CATEGORY_PROJECT = 1
    CATEGORY_USER = 2
    CATEGORY_CHOICES = (
        (CATEGORY_PROJECT, "Project related"),
        (CATEGORY_USER, "User related"),
    )

    category = models.PositiveSmallIntegerField(
        max_length=200, choices=CATEGORY_CHOICES, default=CATEGORY_USER)
    name = models.CharField(max_length=200)
    url = models.CharField(
        max_length=2000, help_text='The main URL of the web resource')

    class Meta:
        verbose_name = _('web resource domain')
        verbose_name_plural = _('web resource domains')


class URLPrefix(Audit):
    """A base URL of a commonly used resources.
    E.g. http or https
    """
    slug = models.SlugField(default="Custom Link")
    base_url = models.CharField(
        max_length=2000, help_text=_("The start of an allowed url (to be "
                                     "joined to an actual url)"))

    class Meta:
        verbose_name = _('URL prefix')
        verbose_name_plural = _('URL prefixes')


class WebResource(Audit):
    """A URI pointing to any web-accessible resource.
    """
    prefix = models.ForeignKey(URLPrefix, editable=False)
    suffix = models.CharField(max_length=2000)

    class Meta:
        app_label = 'pythia'
        verbose_name = _("web resource")
        verbose_name_plural = _("web resources")

    def clean(self):
        fragments = self.suffix.split("/", 3)
        prefix = "/".join(fragments[:3]) + "/"
        suffix = fragments[3]
        if not self.base and URLPrefix.objects.filter(
                base_url__iexact=prefix).exists():
            self.prefix = URLPrefix.objects.get(base_url__iexact=prefix)
        elif not self.base:
            self.prefix = URLPrefix.objects.create(base_url=prefix)
        self.suffix = suffix

    @property
    def url(self):
        return self.prefix + self.suffix


class UserManager(BaseUserManager):
    def __init__(self):
        super(BaseUserManager, self).__init__()
        self.model = 'pythia.User'  # get_user_model()

    def _create_user(self, username, password, is_staff, is_superuser,
                     **extra_fields):
        now = timezone.now()
        user = self.model(username=username, is_staff=is_staff,
                          is_active=True, is_superuser=is_superuser,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields = extra_fields or {}
        extra_fields.setdefault('email', email)
        return self._create_user(username, password, True, False,
                                 **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        return self._create_user(username, password, True, True,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A custom user model for SDIS. Mostly intended to make profile modification
    simpler and less "broken" (seeing a lot of "create profile if it doesn't
    exist") comments littered throughout the code.

    A user can have contact details, affiliations, research profiles and
    publications.
    """
    username = models.CharField(
        _('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[validators.RegexValidator(r'^[\w.@+-]+$',
                    _('Enter a valid username.'), 'invalid')])

# Internal person
# Internal group
# External person
# External group
# Title: everyone if they have it
# Affiliation: everyone if not none or ""

    # Name -------------------------------------------------------------------#
    title = models.CharField(
        max_length=30,
        null=True, blank=True,
        verbose_name=_("Academic Title"),
        help_text=_("Optional academic title, shown in team lists only if "
                    "supplied, and only for external team members."))

    first_name = models.CharField(
    	max_length=100,
        null=True, blank=True,
        verbose_name=_("First Name"),
        help_text=_("First name or given name."))

    middle_initials = models.CharField(
        max_length=100,
        null=True, blank=True,
        verbose_name=_("Initials"),
        help_text=_("Initials of first and middle names. Will be used in "
                    "team lists with abbreviated names."))

    last_name = models.CharField(
        max_length=100,
        null=True, blank=True,
        verbose_name=_("Last Name"),
        help_text=_("Last name or surname."))

    is_group = models.BooleanField(
        default=False,
        verbose_name=_("Show as Group"),
        help_text=_("Whether this profile refers to a group, rather than a "
                    "natural person. Groups are referred to with their group "
                    "name,  whereas first and last name refer to the group's"
                    " contact person."))

    group_name = models.CharField(
        max_length=200,
        null=True, blank=True,
        verbose_name=_("Group name"),
        help_text=_("Group name, if this profile is not a natural "
                    "person. E.g., 'Goldfields Regional Office'."))

    affiliation = models.CharField(
        max_length=200,
        null=True, blank=True,
        verbose_name=_("Affiliation"),
        help_text=_("Optional affiliation, not required for DPaW."
                    " If provided, the affiliation will be appended to the"
                    " person or group name in parentheses."))

    # Contact details --------------------------------------------------------#
    image = models.ImageField(
        upload_to="profiles", null=True, blank=True,
        help_text=_("If you wish, provide us with a face to the name!"))

    email = models.EmailField(
        _('email address'), null=True, blank=True)

    phone = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name=_("Primary Phone number"),
        help_text=_("The primary phone number during work hours."))

    phone_alt = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name=_("Alternative Phone number"),
        help_text=_("An alternative phone number during work hours."))

    fax = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name=_("Fax number"),
        help_text=_("The fax number."))

    # Affiliation: spatial, organizational -----------------------------------#
    program = models.ForeignKey(
        Program, blank=True, null=True,  # optional for migrations
        help_text=_("The main Science and Conservation Division Program "
                    "affilitation."))

    work_center = models.ForeignKey(
        WorkCenter, null=True, blank=True,
        help_text=_("The work center where most time is spent. Staff only."))

    # Academic profile -------------------------------------------------------#
    profile_text = Html2TextField(
        blank=True, null=True,
        help_text=_("A profile text for the staff members, roughly three "
                    "paragraphs long."))

    expertise = Html2TextField(
        blank=True, null=True,
        help_text=_("A bullet point list of skills and expertise."))

    curriculum_vitae = Html2TextField(
        blank=True, null=True,
        help_text=_("A brief curriculum vitae of academic qualifications and "
                    "professional memberships."))

    projects = Html2TextField(
        blank=True, null=True,
        verbose_name=_("Projects outside SDIS"),
        help_text=_("Tell us about your other projects outside SDIS."))

    # Publications -----------------------------------------------------------#
    # Publications should be models in their own module really
    author_code = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name=_("Author code"),
        help_text=_("The author code links users to their publications. "
                    "Staff only."))

    publications_staff = Html2TextField(
        blank=True, null=True,
        verbose_name=_("Staff publications"),
        help_text=_("A list of publications produced for the Department. "
                    "Staff only."))

    publications_other = Html2TextField(
        blank=True, null=True,
        verbose_name=_("Other publications"),
        help_text=_("A list of publications produced under external "
                    "affiliation, in press or otherwise unregistered as "
                    "staff publication."))

    # Administrative details -------------------------------------------------#
    is_staff = models.BooleanField(
        _('staff status'), default=True,
        help_text=_("Designates whether the user can log into this admin "
                    "site."))

    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts."))

    is_external = models.BooleanField(
        default=False,
        verbose_name=_("External to DPaW"),
        help_text=_("Is the user external to DPaW?"))

    agreed = models.BooleanField(
        default=False, editable=False,
        verbose_name=_("Agreed to the Terms and Conditions"),
        help_text=_("Has the user agreed to SDIS' Terms and Conditions?"))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    DEFAULT_GROUP = 'Users'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self, *args, **kwargs):
        """
        Try to add the user to the default group on save.
        """
        created = True if not self.pk else False

        if not self.middle_initials:
            try:
                self.middle_initials = self.guess_first_initial()
            except:
                logger.warning("Something went wrong trying to guess"
                               " the initials from first name")

        super(User, self).save(*args, **kwargs)

        if created:
            try:
                group = Group.objects.get(name__iexact=self.DEFAULT_GROUP)
            except Group.DoesNotExist:
                logger.warning("Failed to assign group `%s' to user `%s', "
                               "group does not exist." % (
                                   self.DEFAULT_GROUP, self.email))
            else:
                self.groups.add(group)

    def get_title(self):
        """Return the title if supplied and user is_external.

        SANITY WARNING this function will HIDE the title for internal staff
        """
        return self.title if (self.title and self.is_external) else ""

    def get_middle_initials(self):
        i = self.middle_initials if self.middle_initials else ""
        if len(i) > 1:
            return i[1:]
        else:
            return ""

    def guess_first_initial(self):
        return self.first_name[0] if self.first_name else ""

    def get_affiliation(self):
        "Return the affiliation in parentheses if provided, or an empty string."
        a = "({0})".format(self.affiliation) if self.affiliation else ""
        return a

    @property
    def fullname(self):
        return self.get_full_name()

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        if self.is_group:
            full_name = "{0} {1}".format(self.group_name, self.get_affiliation())
        else:
            full_name = "{0} {1} {2} {3} {4}".format(
                self.get_title(),
                self.first_name,
                self.get_middle_initials(),
                self.last_name,
                self.get_affiliation())
        return full_name.strip()

    @property
    def short_name(self):
        return self.first_name if self.first_name else self.fullname

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    @property
    def abbreviated_name(self):
        return self.get_abbreviated_name()

    def get_abbreviated_name(self):
        """
        If initials are supplied, returns initials and surname, else
        given name and surname.
        """
        if self.is_group:
            return self.get_full_name()
        else:
            full_name = "{0} {1} {2} {3}".format(
                    self.get_title(),
                    self.middle_initials,  # remember these are full initials
                    self.last_name,
                    self.get_affiliation())
        return full_name.strip()

    @property
    def abbreviated_name_no_affiliation(self):
        return self.get_abbreviated_name_no_affiliation()

    def get_abbreviated_name_no_affiliation(self):
        """
        If initials are supplied, returns initials and surname, else
        given name and surname.
        """
        if self.is_group:
            return self.get_full_name()
        else:
            full_name = "{0} {1} {2}".format(
                    self.get_title(),
                    self.middle_initials,  # remember these are full initials
                    self.last_name)
        return full_name.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        slug = " ({0}-{1})".format(self.program.cost_center,
                                   self.program.slug) if self.program else ""
        return "{0}{1}".format(self.get_full_name(), slug)

    @property
    def supervisor(self):
        """
        Returns the Program Leader as User object, falls back to the User.
        """
        return self.program.program_leader if self.program else self

    @property
    def registration_complete(self):
        """
        Returns True if the user is registered, but not yet cleared to use the
        site.
        """
        if self.user.is_superuser:
            return False
        return self.is_external and not self.is_staff

    @property
    def tasklist(self):
        """
        Returns documents which require input from the current user.
        """
        from pythia.projects.models import Project, ProjectMembership
        from pythia.documents.models import Document, ProjectPlan

        groups = [g.name for g in self.groups.all()]
        is_bm = u'BM' in groups
        is_hc = u'HC' in groups
        is_ae = u'AE' in groups
        is_scd = u'SCD' in groups

        excludes = set()
        # Project Plans pending endorsement/approval
        pplan_list = ProjectPlan.objects.filter(
                project__status=Project.STATUS_PENDING)
        for doc in pplan_list:
            if (doc.bm_endorsement == Document.ENDORSEMENT_REQUIRED) or (
                doc.hc_endorsement == Document.ENDORSEMENT_REQUIRED) or (
                doc.ae_endorsement == Document.ENDORSEMENT_REQUIRED):
                excludes.add(doc)

        endorsements = set()

        if is_bm:
            print(type(pplan_list))
            endorsements.update(pplan_list.filter(
                bm_endorsement=Document.ENDORSEMENT_REQUIRED
            ).select_related('project'))

        if is_hc:
            endorsements.update(pplan_list.filter(
                hc_endorsement=Document.ENDORSEMENT_REQUIRED
            ).select_related('project'))

        if is_ae:
            endorsements.update(pplan_list.filter(
                ae_endorsement=Document.ENDORSEMENT_REQUIRED
            ).select_related('project'))

        approvals = set()

        program_list = self.leads_programs.all()
        # program -> projects is a reverse foreign key lookup,
        # we can't batch this, so do one query per program
        for prog in program_list:
            projects = prog.project_set.prefetch_related('documents')
            for proj in projects:
                approvals.update(proj.documents.filter(
                    status=Document.STATUS_INREVIEW
                    ).select_related('project'))

        member_list = ProjectMembership.objects.prefetch_related(
                'project', 'project__documents').filter(user=self)

        for member in member_list:
            approvals.update(member.project.documents.filter(
                status=Document.STATUS_NEW).select_related('project'))

        if is_scd:
            documents = Document.objects.filter(
                    status=Document.STATUS_INREVIEW).select_related('project')
            # right now the can_approve method of most document classes is
            # just True.
            # if there's any logic that does heavy lookups, it may pay to
            # add more prefetch arguments to the above query
            documents = set([d for d in documents if d.can_approve()])
            approvals.update(documents)

        #  remove all the endorsements from the approvals pool
        approvals.difference_update(excludes)

        # TODO: presort the output lists by descending project ID
        return {'approvals': list(approvals),
                'endorsements': list(endorsements),
                'count': len(approvals)+len(endorsements)}

    @property
    def portfolio(self):
        """
        Returns projects of various types which current user supervises or
        participates in.

        Required for index.html's My Tasks/Projects/Collaborations.
        If it's just for index.html (a template) consider making it a template
        tag!
        """
        from pythia.projects.models import (
            Project, ProjectMembership, ScienceProject, CoreFunctionProject,
            CollaborationProject, StudentProject)
        from pythia.documents.models import (ConceptPlan, ProjectPlan)
        from datetime import datetime, timedelta

        # Fun fact: Django polymorphism casts the returned items from a
        # Project.objects query into the highest subclass, but does not
        # rig it for private key lookups. This is why we need to hit the
        # database again with pm_list to fetch the correctly casted object.

        best_before = datetime.now() - timedelta(days=30)
        pm_list = ProjectMembership.objects.select_related("project").order_by(
                    "-project__year", "-project__number").filter(
                user=self, project__status__in=Project.ACTIVE)
        projects = Project.objects.order_by("-year", "-number").filter(
            project_owner=self)
        own_list = projects.filter(status__in=Project.ACTIVE)
        stuck_new = projects.filter(
            status__in=Project.STATUS_NEW, created__lt=best_before)
        stuck_pending = projects.filter(
            status__in=Project.STATUS_PENDING, created__lt=best_before)
        result = {"projects": {}, "collabs": {}, "stuck": {}}
        proj_result = {"super": [], "regular": []}
        collab_result = {"super": [], "regular": []}
        stuck_result = {"new": [], "pending": []}

        for x in stuck_new:
            # Projects stuck in approval for more than three months need a
            # kick up the rear end
            doc = x.documents.instance_of(ConceptPlan).get()
            stuck_result["new"].append(doc)

        for x in stuck_pending:
            doc = x.documents.instance_of(ProjectPlan).get()
            stuck_result["pending"].append(doc)

        for x in own_list:
            if x.type in (
                    Project.SCIENCE_PROJECT, Project.CORE_PROJECT):
                proj_result["super"].append(x)
            elif x.type in (
                    Project.COLLABORATION_PROJECT, Project.STUDENT_PROJECT):
                collab_result["super"].append(x)

        for x in pm_list:
            res = None
            proj = None

            if x.project.type == Project.SCIENCE_PROJECT:
                res = proj_result
                proj = ScienceProject.objects.get(pk=x.project.pk)
            elif x.project.type == Project.CORE_PROJECT:
                res = proj_result
                proj = CoreFunctionProject.objects.get(pk=x.project.pk)
            elif x.project.type == Project.COLLABORATION_PROJECT:
                res = collab_result
                proj = CollaborationProject.objects.get(pk=x.project.pk)
            elif x.project.type == Project.STUDENT_PROJECT:
                res = collab_result
                proj = StudentProject.objects.get(pk=x.project.pk)
            else:
                continue

            if x.role == ProjectMembership.ROLE_SUPERVISING_SCIENTIST:
                if proj in res["super"]:
                    continue
                else:
                    res["super"].append(proj)
            else:
                res["regular"].append(proj)

        if proj_result["super"] or proj_result["regular"]:
            result["projects"] = proj_result

        if collab_result["super"] or collab_result["regular"]:
            result["collabs"] = collab_result

        if stuck_result["new"] or stuck_result["pending"]:
            result["stuck"] = stuck_result

        return result
