# import logging
# logger = logging.getLogger(__name__)
#
#
# def migrate_projects_to_html(debug=False):
#     """Convert selected fields from markdown to storing HTML.
#
#     * Converts md tables in Conceptplan.staff and .budget
#     * Converts project names
#     """
#     from pythia.projects import models as m
#     from pythia.utils import text2html
#     for p in m.Project.objects.all():
#         logger.debug("Converting {0}".format(p))
#         p.title = text2html(p.title)
#         p.save()
#         logger.info("converted title of {0}".format(p))
