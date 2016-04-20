[![wercker status](https://app.wercker.com/status/9a7a620f6caa6ce1ae7624c12a06fb48/m "wercker status")](https://app.wercker.com/project/bykey/9a7a620f6caa6ce1ae7624c12a06fb48)
[![Stories in Ready](https://badge.waffle.io/parksandwildlife/sdis.svg?label=ready&title=Ready)](http://waffle.io/parksandwildlife/sdis)

Science Directorate Information System
======================================
The Science and Conservation Directorate Information System v3 (SDIS) is a divisional Annual Reporting and Science project documentation Environment. Its main module "Pythia" is named after the priestess at the heart of the Greek oracle of Delphi, whose comments and approvals were used as an early project planning tool.

Development
-----------

`fab test` run tests

`fab shell` run shell\_plus

`fab run` run app on localhost:5000


Deployment
----------

`fab hammertime` reset and recreate db

`fab sexytime` Migrate data from production snapshot (not included)


