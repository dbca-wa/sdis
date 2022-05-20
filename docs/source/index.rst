******************
SDIS Documentation
******************

.. image:: https://circleci.com/gh/dbca-wa/sdis.svg?style=svg
   :target: https://circleci.com/gh/dbca-wa/sdis
   :alt: Test Status
.. image:: https://coveralls.io/repos/github/dbca-wa/sdis/badge.svg?branch=master
   :target: https://coveralls.io/github/dbca-wa/sdis
   :alt: Test Coverage
.. image:: https://img.shields.io/github/issues/dbca-wa/sdis
   :target: https://github.com/dbca-wa/sdis/projects/1
   :alt: GitHub issues

The Science Directorate Information System (SDIS) is DBCA's project documentation,
approval and reporting platform.

Documentation for common SDIS workflows is split by user role:

* :ref:`authors`: Research Scientists and their colleagues create Projects and are primary authors of Project documentation.
* :ref:`reviewers`: Program Leaders, Regional Leaders, Branch Managers and equivalent heads of SDIS Programs review Project documentation.
* :ref:`approvers`: Directors as heads of SDIS Divisons approve Project documentation.
* :ref:`administrators`: SDIS Administrators act system wide with unrestricted permissions.

See also :doc:`faq`.
The above should enable SDIS users to fulfil their tasks and operate SDIS.

Interested readers may learn from the :doc:`specs` in full detail about the
User roles (governing permissions and available actions), and how to advance 
projects through their life cycles through document approvals.

In tech speak, every feature, button, and workflow of SDIS should be defined in
the :doc:`specs`, we should have a test case covering each requirement
and most of the application code (badge "Test Coverage"),
and all tests should pass (badge "Test Status").

Installing, running and maintaining SDIS is documented in the :doc:`maintainer_docs`;
the software architecture and design decisions are discussed in the :doc:`developer_docs`.

.. toctree::
   :maxdepth: 3

   authors
   reviewers
   approvers
   administrators
   faq
   quickstart
   specs
   maintainer_docs
   developer_docs
