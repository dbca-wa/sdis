from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db.models.signals import post_syncdb
import logging

logger = logging.getLogger(__name__)


def update_document_permissions(document):
    """
    This method assigns document permissions on demand.

    document.project.members can submit_* and change_* (per object)
    group SMT can review_* (per class)
    group SCD can approve_* (per class)
    """
    # Avoid cyclic dependency by importing inside method
    from guardian.shortcuts import assign_perm
    from guardian import models as gm

    # TODO: handle removing permissions too.
    opts = document._meta
    logger.info("Post-save: Updating permissions for document {0}".format(
        document.__str__()))

    for action in ["submit", "change"]:
        codename = "{0}.{1}_{2}".format(opts.app_label, action, opts.model_name)

        for user in document.project.members.all():
            logger.info("Assigning user {0} permission {1}".format(
                user.pk, codename))
            assign_perm(codename, user, document)

def add_document_permissions(sender, **kwargs):
    """
    Create permissions for all document models.

    Hooked up to run once post-syncdb.
    Reason for adding permissions: Permissions need to exist before they can be
    allocated to users and groups.

    Also allocates permissions "submit", "review", "approve" to Directorate group;
    allocates permissions "submit" and "review" to SMT group.

    Permissions are deliberately allocated including lower tier permissions.
    Alternatively, Directorate could only get permission "approve" and
    SMT could only get "review".

    Project members have object level permissions set in
    `update_document_permissions`.
    """
    from django.contrib.auth.models import Group
    from guardian.shortcuts import assign_perm

    users, created = Group.objects.get_or_create(name='Users')
    smt, created = Group.objects.get_or_create(name='SMT')
    scd, created = Group.objects.get_or_create(name='SCD')

    for content_type in ContentType.objects.filter(app_label='documents'):
        for action in ["submit", "review", "approve"]:
            codename = "%s_%s" % (action, content_type.model)

            p, created = Permission.objects.get_or_create(
                content_type=content_type, codename=codename,
                name="Can %s %s" % (action, content_type.name))

            scd.permissions.add(p)

            if action != "approve":
                smt.permissions.add(p)

def setup_user_permissions(sender, **kwargs):
    """
    Set up the default user's permissions. This allows a standard user the
    ability to create projects.
    """
    from django.contrib.auth.models import Group

    group, created = Group.objects.get_or_create(name='Users')

    permissions = (
        ('add_project', 'projects', 'project'),
        ('add_scienceproject', 'projects', 'scienceproject'),
        ('add_corefunctionproject', 'projects', 'corefunctionproject'),
        ('add_collaborationproject', 'projects', 'collaborationproject'),
        ('add_studentproject', 'projects', 'studentproject'),

        ('change_project', 'projects', 'project'),
        ('change_scienceproject', 'projects', 'scienceproject'),
        ('change_corefunctionproject', 'projects', 'corefunctionproject'),
        ('change_collaborationproject', 'projects', 'collaborationproject'),
        ('change_studentproject', 'projects', 'studentproject'),

        #('submit_project', 'projects', 'project'),
        #('submit_scienceproject', 'projects', 'scienceproject'),
        #('submit_corefunctionproject', 'projects', 'corefunctionproject'),
        #('submit_collaborationproject', 'projects', 'collaborationproject'),
        #('submit_studentproject', 'projects', 'studentproject'),

        #('review_project', 'projects', 'project'),
        #('review_scienceproject', 'projects', 'scienceproject'),
        #('review_corefunctionproject', 'projects', 'corefunctionproject'),
        #('review_collaborationproject', 'projects', 'collaborationproject'),
        #('review_studentproject', 'projects', 'studentproject'),

        #('approve_project', 'projects', 'project'),
        #('approve_scienceproject', 'projects', 'scienceproject'),
        #('approve_corefunctionproject', 'projects', 'corefunctionproject'),
        #('approve_collaborationproject', 'projects', 'collaborationproject'),
        #('approve_studentproject', 'projects', 'studentproject'),

        ('add_conceptplan', 'documents', 'conceptplan'),
        ('add_projectplan', 'documents', 'projectplan'),
        ('add_progressreport', 'documents', 'progressreport'),
        ('add_studentreport', 'documents', 'studentreport'),
        ('add_projectclosure', 'documents', 'projectclosure'),

        # DO NOT allow users to change any Document unless allowed per object
        #('change_conceptplan', 'documents', 'conceptplan'),
        #('change_projectplan', 'documents', 'projectplan'),
        #('change_progressreport', 'documents', 'progressreport'),
        #('change_studentreport', 'documents', 'studentreport'),
        #('change_projectclosure', 'documents', 'projectclosure'),
    )

    for codename, app_label, model in permissions:
        # This should only be run once, after all models and content types
        # have been set up. Something spooky going on, requires investigation.
        try:
            permission = Permission.objects.get_by_natural_key(codename,
                app_label, model)
            group.permissions.add(permission)
        except:
            pass


# Comment out before loaddata of production data in dev/test/uat
# post_syncdb.connect(add_document_permissions, dispatch_uid='add_document_permissions')
# post_syncdb.connect(setup_user_permissions, dispatch_uid='setup_user_permissions')


def migrate_documents_to_html(debug=False):
    """Convert selected fields from markdown to storing HTML.

    * Converts project names.

    See also `migrate_html_tables_to_arrays` for migration of tables.
    """
    from pythia.documents import models as m
    from pythia.utils import extract_md_tables, text2html

    for d in m.Document.objects.all():
        if d._meta.model_name == 'conceptplan':
            if debug: print("Converting {0}".format(d))
            d.summary = text2html(d.summary)
            d.outcome = text2html(d.outcome)
            d.collaborations = text2html(d.collaborations)
            d.strategic = text2html(d.strategic)
            d.budget = extract_md_tables(d.budget)
            d.staff = extract_md_tables(d.staff)
            d.save()
            action = 'Converted'

        elif d._meta.model_name == 'projectplan':
            d.backgorund = text2html(d.background)
            d.aims = text2html(d.aims)
            d.outcome = text2html(d.outcome)
            d.knowledge_transfer = text2html(d.knowledge_transfer)
            d.project_tasks = text2html(d.project_tasks)
            d.references = text2html(d.references)
            d.methodology = text2html(d.methodology)
            d.no_specimens = text2html(d.no_specimens)
            d.data_management = text2html(d.data_management)
            #d.operating_budget = extract_md_tables(d.operating_budget)
            d.save()
            action = 'Converted'


        elif d._meta.model_name == 'progressreport':
            d.context = text2html(d.context)
            d.aims = text2html(d.aims)
            d.progress = text2html(d.progress)
            d.implications = text2html(d.implications)
            d.future = text2html(d.future)
            d.save()
            action = 'Converted'

        elif d._meta.model_name == 'studentreport':
            d.progress_report = text2html(d.progress_report)
            d.save()
            action = 'Converted'

        else:
            action = "Skipping"

        # Common actions
        msg= "{0} {1}".format(action, d)
        if debug: print(msg)
        logger.info(msg)



def html_table_to_array(html_string):
    """Converts an HTML table to a list of lists.
    """
    from bs4 import BeautifulSoup as BS
    import json
    if (len(BS(html_string).findAll("tr")) > 0 and
        html_string is not None and html_string is not ""):
        return json.dumps([[cell.string or '' for cell in row.findAll("td")]
            for row in BS(html_string).findAll("tr")])
    else:
        return html_string


def migrate_html_tables_to_arrays(debug=False):
    """Converts all existing tables from HTML to list of lists.

    This function is to be run once only when switching
    from storing markdown in the database to storing HTML.
    """
    from pythia.documents import models as m
    from pythia.utils import extract_md_tables, text2html

    for d in m.Document.objects.all():
        if d._meta.model_name == 'conceptplan':
            if debug: print("Converting {0}".format(d))
            d.budget = html_table_to_array(d.budget)
            d.staff = html_table_to_array(d.staff)
            d.save()
            action = 'Converted'

        # There are no populated budgets yet!
        #elif d._meta.model_name == 'projectplan':
        #    if debug: print("Converting {0}".format(d))
        #    d.operating_budget = html_table_to_array(d.operating_budget)
        #    d.save()
        #    action = 'Converted'

        else:
            action = "Skipping"

        # Common actions
        msg= "{0} {1}".format(action, d)
        if debug: print(msg)
        logger.info(msg)
