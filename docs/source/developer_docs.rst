***********************
Developer Documentation
***********************

This chapter discusses the design philosophy behind the software architecture of SPMS.
To get up and running in your own development environment, consult the
`README <https://github.com/dbca-wa/sdis>`_.

Polymorphic inheritance
=======================

Projects and documents are implemented using django-polymorphic data model
inheritance. This allows us to easily extend a base model with all the common
fields, but more importantly, it allows us to reduce duplication of shared business logic.

Problems arise when combining with other packages, e.g. django-fsm transitions
can be inherited, but the user permissions need to match the exact data model.


Finite State Machine
====================

Product life cycle management for projects and documents is implemented with
django-fsm, which contributes a set transition graph, gate checks, pre and post
transition signals, and user level permissions (to be used with caution on
polymorphic models).


Permissions
===========

The business logic of finding and linking audiences to actions is kept in the
transition permissions, which are lambda functions calling the instance's
"submitter", "reviewer" and "approver" functions, which "know" the correct
audiences. This keeps the business logic inside the document and project
models.

* Everyone is allowed to "view"
* Project teams are allowed to "change" project and document details
* Project teams are allowed to "submit" documents for review,
  retract them, and request project closure.
* All SCMT members (program leaders) are allowed to "review" documents
* All Directorate representatives are allowed to "approve" things and fast-track
  projects through their life cycles to re-align SPMS with reality.

Notably, there are no customisations to Django permissions in place.
Django-fsm accepts either hard-coded permission strings, or lambda functions.

Hard-coded permission strings are referred from django_fsm's has_perm to
django.contrib.auth.models.PermissionMixin's has_perm, which requires properly
named "app.permission_model" permissions. The "model" part is hard-coded, and
will not be correct if the transition is inherited to a polymorphic child model.
This will prevent permission strings to be used.

Lambda functions however can accept arguments, such as model functions declared as
properties. Properties can be inherited, and overwritten in child models where
necessary. This means that lambda functions used in transition permissions can
be inherited without problems. An added benefit is the somewhat cleaner design
of keeping the definition and source of permissions together with the transitions
with the model.

Finding the right audience for notifications and write permissions
------------------------------------------------------------------

To restrict editing of documents to the correct audience,
`pythia.documents.admin.DocumentAdmin.get_readonly_fields` refers to
`Document.get_users_with_change_permissions()`, which in turn returns the
audience corresponding to its status.

The current implementation permits the respectively involved users and their line
management to edit documents.

This keeps the business logic with the field `status` it depends on at the model.
The previous implementation to use post-save signals setting (custom) document permissions,
and letting views determine read-only fields from these permissions, was more indirect,
extremely error-prone and hard to understand.


Django Admin
============

Building the UI from the Django admin saves some development time, as Django admin
already provides CRUD views.
However, it takes away the "plain old admin backdoor", takes away human-readable URLs,
requires some advanced workarounds and overrides, and inflicts another layer of complexity.

In retrospect, using Django's admin interface as front-end will work beautifully
for simple CRUD applications, but cause far more trouble than time savings
when trying to design, maintain, and evolve a highly complex application
with ever-changing requirements to the UI and workflows.

API
===

Planned, needed, coming up.


Continuous Integration and TDD
==============================

After four years of "scraping over the line" in "whatever it takes" mode, we now
finally are implementing Test Driven Development. See the badges on GitHub and
at the top of this documentation for current build status and test coverage.

The ideal development work flow
-------------------------------
* Translate feature requests by stakeholders into functional specs
* Translate functional specs into tests
* Write code, add docstrings
* Document intended usage of new fatures in user docs
* Add/adjust UI elements, feature tours (joyride.js), tooltips


Testing
=======

Objects and database persistence
--------------------------------

One intriguing bug we found had us scratching our heads for longer than we liked.
Consider a test case involving a Project subclass, e.g. ScienceProject.
ScienceProjects have transitions, which spawn subclasses of Documents, which
have their own transitions. A Document's final "approve" transition will trigger
the corresponding transition on their Project object.

On one hand, accessing the attributes of the document's FK to the project (`d.project`)
will fetch the new, changed project from memory.

On the other hand, accessing the project directly will fetch the old, unchanged
object fresh from the database. It will appear as the transitions had no effect.

To synchronise db and memory, the reference to the project has to be saved to db.
::

    p = ScienceProjectFactory.create()
    d = p.documents.instance_of(ConceptPlan).get()
    d.first_transition()
    d.next_transition()
    d.final_transition_that_triggers_project_transition()

    # p is unchanged
    self.assertEqual(p.status, UNCHANGED_STATUS)
    # d.project is changed
    self.assertEqual(d.project.status, CHANGED_STATUS)
    p = d.project
    p.save()

    self.assertEqual(p.status, CHANGED_STATUS)


.. Data models
.. ===========
..
.. These data models are auto-generated with each commit.
..
.. .. image:: img/dm_projects.svg
..    :alt: pythia.projects data model
..
.. .. image:: img/dm_documents.svg
..    :alt: pythia.documents data model
..
.. .. image:: img/dm_reports.svg
..    :alt: pythia.reports data model
..
.. .. image:: img/dm_pythia.svg
..    :alt: pythia data model


***********************
Technical Documentation
***********************

This chapter links automatically extracted code documentation with the source code.

**NOTE** Until SPMS is upgraded to Django 1.8, autodocs will fail to extract
docstrings from modules using Django image fields and django-fsm state fields.
Refer directly to the docstrings inside code if they don't show up below.

pythia Package
==============

:mod:`pythia.widgets` Module
---------------------------------------

.. automodule:: pythia.widgets
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`pythia.models` Module
---------------------------

Custom User model
^^^^^^^^^^^^^^^^^
A custom User model provides

.. autoclass:: pythia.models.User
    :members:
    :undoc-members:
    :show-inheritance:

Custom model mixins and managers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Coming soon.


:mod:`pythia.documents.models` Module
---------------------------------------

.. automodule:: pythia.documents.models
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`pythia.documents.admin` Module
---------------------------------------

.. automodule:: pythia.documents.admin
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`pythia.documents.templatetags.documents` Module
-----------------------------------------------------

.. automodule:: pythia.documents.templatetags.documents
    :members:
    :undoc-members:
    :show-inheritance:
