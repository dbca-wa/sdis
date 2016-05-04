[![Build status](https://app.wercker.com/status/e3bc48bfd0360930f22bd083282f7b07/s "wercker status")](https://app.wercker.com/project/bykey/e3bc48bfd0360930f22bd083282f7b07)
[![Things to do](https://badge.waffle.io/parksandwildlife/sdis.svg?label=ready&title=Ready)](http://waffle.io/parksandwildlife/sdis)

Science Directorate Information System
======================================
The Science and Conservation Directorate Information System v3 (SDIS) is a
divisional Annual Reporting and Science project documentation Environment.
Its main module "pythia" is named after the priestess at the heart of the
Greek oracle of Delphi, whose comments and approvals were used as an early
project planning tool.

Development
-----------

* `fab test` run tests
* `fab shell` run shell\_plus
* `fab go` run app on localhost:5000

Deployment
----------

* Rename `.env.template` to `.env`, enter your confidential settings.
* Run `fab deploy`.
* Set file permissions and ownership (media, logs) for code
* Create a supervisor config following `sdis.conf.template`
* Run SDIS in production mode with `honcho start`, or orchestrate with supervisor
  
