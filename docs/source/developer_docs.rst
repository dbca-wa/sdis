***********************
Developer Documentation
***********************

This chapter discusses the design philosophy behind the software architecture of SDIS.
To get up and running in your own development environment, consult the
`README<https://github.com/parksandwildlife/sdis>`_.

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

Admin interface
===============

Using the admin interface saves some development time, as it provides CRUD views.
However, it takes away the "plain old admin backdoor", requires some advanced
workarounds and overrides, and inflicts another layer of complexity.
In retrospect, using Django's admin interface as front-end will work beautifully
for simple CRUD applications, but cause serious trouble when trying to design,
maintain, and evolve a very custom, highly complex application.

API
===

Planned, needed, coming up.


Continuous Integration and TDD
==============================

After four years of "scraping over the line" in "whatever it takes" mode, we now
finally are implementing Test Driven Development. See the badges on GitHub and
at the top of this documentation for current build status and test coverage.


Data models
===========

These data models are auto-generated with each commit.

.. image:: img/dm_projects.svg
   :alt: pythia.projects data model

.. image:: img/dm_documents.svg
   :alt: pythia.documents data model

.. image:: img/dm_reports.svg
   :alt: pythia.reports data model

.. image:: img/dm_pythia.svg
   :alt: pythia data model


***********************
Technical Documentation
***********************

Tests
=====
:mod:`test_functional` Module
-----------------------------

.. automodule:: pythia.tests.test_functional
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`test_models` Module
-------------------------

.. automodule:: pythia.tests.test_models
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`test_unit` Module
-----------------------

.. automodule:: pythia.tests.test_unit
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`test_views` Module
------------------------

.. automodule:: pythia.tests.test_views
    :members:
    :undoc-members:
    :show-inheritance:
