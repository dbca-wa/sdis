******************
SPMS Documentation
******************

.. image:: https://circleci.com/gh/dbca-wa/SPMS.svg?style=svg
   :target: https://circleci.com/gh/dbca-wa/SPMS
   :alt: Test Status
.. image:: https://coveralls.io/repos/github/dbca-wa/SPMS/badge.svg?branch=master
   :target: https://coveralls.io/github/dbca-wa/SPMS
   :alt: Test Coverage
.. image:: https://img.shields.io/github/issues/dbca-wa/SPMS
   :target: https://github.com/dbca-wa/SPMS/projects/1
   :alt: GitHub issues

The Science Project Management System (SPMS) is DBCA's project documentation,
approval and reporting platform.

Documentation for common SPMS workflows is split by user role:

* :ref:`authors`: Research Scientists and their colleagues create Projects and are primary authors of Project documentation.
* :ref:`reviewers`: Program Leaders, Regional Leaders, Branch Managers and equivalent heads of SPMS Programs review Project documentation.
* :ref:`approvers`: Directors as heads of SPMS Divisons approve Project documentation.
* :ref:`administrators`: SPMS Administrators act system wide with unrestricted permissions.

See also :doc:`faq`.
The above should enable SPMS users to fulfil their tasks and operate SPMS.

If you need help or contact anyone about a specific Project or Document in SPMS,
please make their lives easier and include the URL to the Project or Document. 
The URL is shown in your browser when you look at the thing you have a question about and starts with ``https://scienceprojects.dbca.wa.gov.au/``.

Interested readers may learn from the :doc:`specs` in full detail about the
User roles (governing permissions and available actions), and how to advance 
projects through their life cycles through document approvals.

In tech speak, every feature, button, and workflow of SPMS should be defined in
the :doc:`specs`, we should have a test case covering each requirement
and most of the application code (badge "Test Coverage"),
and all tests should pass (badge "Test Status").

Installing, running and maintaining SPMS is documented in the :doc:`maintainer_docs`;
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
