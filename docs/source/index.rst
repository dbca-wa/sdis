******************
SDIS Documentation
******************

.. image:: https://circleci.com/gh/dbca-wa/sdis.svg?style=svg
   :target: https://circleci.com/gh/dbca-wa/sdis
   :alt: Test Status
.. image:: https://coveralls.io/repos/github/dbca-wa/sdis/badge.svg?branch=master
   :target: https://coveralls.io/github/dbca-wa/sdis
   :alt: Test Coverage
.. image:: https://badge.waffle.io/dbca-wa/sdis.svg?label=ready&title=Ready
   :target: https://waffle.io/dbca-wa/sdis
   :alt: Tasks

The Science Directorate Information System (SDIS) is the project documentation,
approval and reporting platform for DBCA's Biodiversity Conservation Division.

SDIS users will find answers to their :doc:`faq`,
and instructions on :doc:`quickstart` with the most common tasks.
This should enable any user to fulfill their tasks on SDIS as required.

Interested readers may learn from the :doc:`specs` in full detail about the
User roles (governing permissions and available actions), and how to play the
Monopoly game of advancing projects through their life cycles by solving the
side quests of document approvals.

In tech speak, every feature, button, and workflow of SDIS should be defined in
the :doc:`specs`, we should have a test case covering each requirement
and most of the application code (badge "Test Coverage"),
and all tests should pass (badge "Test Status").

Installing, running and maintaining SDIS is documented in the :doc:`maintainer_docs`;
the software architecture and design decisions are discussed in the :doc:`developer_docs`.

.. toctree::
   :maxdepth: 3

   faq
   quickstart
   specs
   maintainer_docs
   developer_docs
