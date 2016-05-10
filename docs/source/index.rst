******************
SDIS Documentation
******************

.. image:: https://circleci.com/gh/parksandwildlife/sdis.svg?style=svg
   :target: https://circleci.com/gh/parksandwildlife/sdis
   :alt: Test Status
.. image:: https://coveralls.io/repos/github/parksandwildlife/sdis/badge.svg?branch=master
   :target: https://coveralls.io/github/parksandwildlife/sdis
   :alt: Test Coverage
.. image:: https://badge.waffle.io/parksandwildlife/sdis.svg?label=ready&title=Ready
   :target: http://waffle.io/parksandwildlife/sdis
   :alt: Tasks

The Science Directorate Information System (SDIS) is the project documentation,
approval and reporting platform for DPaW's Science and Conservation Division.

SDIS users will find answers to their :doc:`faq`,
and instructions on :doc:`quickstart` with the most common tasks.
This should enable any user to fulfil their tasks on SDIS as required.

Interested readers may learn from the :doc:`specs` in full detail about the
User roles (governing permissions and available actions), and how to play the
Monopoly game of advancing projects through their life cycles by solving the
side quests of document approvals.

In tech speak, every feature, button, and workflow of SDIS should be defined in
the :doc:`specs`, we should have a test case covering each requirement
(badge "Test Coverage"), and all tests should pass (badge "Test Status").

Installing, running and maintaining SDIs is documented in the :doc:`maintainer_docs`;
the sofware architecture and design decisions are discussed in the :doc:`developer_docs`.

.. toctree::
   :maxdepth: 3

   faq
   quickstart
   specs
   maintainer_docs
   developer_docs
