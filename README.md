[![Test Status](https://circleci.com/gh/parksandwildlife/sdis.svg?style=svg)](https://circleci.com/gh/parksandwildlife/sdis)
[![Test Coverage](https://coveralls.io/repos/github/parksandwildlife/sdis/badge.svg?branch=master)](https://coveralls.io/github/parksandwildlife/sdis?branch=master)
[![Open Issues](https://badge.waffle.io/parksandwildlife/sdis.svg?label=ready&title=Ready)](http://waffle.io/parksandwildlife/sdis)

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

CI
---

To setup CI with [circleCI](https://circleci.com), authorise the repo at
circleCI and provide these settings:

* Environment variables:
    * `DJANGO_SETTINGS_MODULE`: `sdis.settings`
    * `DATABASE_URL`: `postgis://ubuntu:@localhost:5432/circle_test`

Notes on `DATABASE_URL`:

* The protocol needs to be `postgis` to override the default `postgres`.
* The value doesn't require quotes.
* The user must be `ubuntu`, no password required.
* The database `circle_test` is already provided, no need to `createdb`.
