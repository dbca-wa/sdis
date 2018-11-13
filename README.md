[![Test Status](https://circleci.com/gh/dbca-wa/sdis.svg?style=svg)](https://circleci.com/gh/dbca-wa/sdis)
[![Coverage Status](https://coveralls.io/repos/github/dbca-wa/sdis/badge.svg?branch=master)](https://coveralls.io/github/dbca-wa/sdis?branch=master)
[![Issues](https://badge.waffle.io/dbca-wa/sdis.svg?label=ready&title=Ready)](http://waffle.io/dbca-wa/sdis)
[![Documentation Status](https://readthedocs.org/projects/sdis/badge/?version=latest)](http://sdis.readthedocs.io/?badge=latest)

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
* Create a supervisor config following `sdis/sdis.conf.template`
* Run SDIS in production mode with `honcho start`, or orchestrate with supervisor

Note: [This bug](https://code.djangoproject.com/ticket/20036) could throw an error like
"django GEOSException: Could not parse version info string 3.6.2-CAPI...".

Patch [django/contrib/gis/geos/libgeos.py](https://github.com/django/django/commit/747f7d25490abc3d7fdb119f0ce3708d450eb4c2#diff-e0475de5c597e1c67bb40752a38f2276)
as follows:
```
 version_regex = re.compile(
     r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<subminor>\d+))'
     r'((rc(?P<release_candidate>\d+))|dev)?-CAPI-(?P<capi_version>\d+\.\d+\.\d+)( .*)?$')
```

Note the changed `( .*)?` group at the end to capture the version hash.

CI
---

To setup CI with [circleCI](https://circleci.com) and
[coveralls.io](https://coveralls.io), authorise the repo with both providers
and provide these settings:

* Environment variables:
    * `DJANGO_SETTINGS_MODULE`: `sdis.settings`
    * `DATABASE_URL`: `postgis://ubuntu:@localhost:5432/circle_test`
    * `COVERALLS_REPO_TOKEN=`: your [coveralls.io](https://coveralls.io) repo token

Notes on `DATABASE_URL`:

* The protocol needs to be `postgis` to override the default `postgres`.
* The `DATABASE_URL` value doesn't require quotes.
* The user must be `ubuntu`, no password is required.
* The database `circle_test` is already provided, no need to `createdb`.

Notes on coverage reports:

* `fab test` analyses coverage
* pushing commits to GitHub lets circleCI generate and push the coverage reports
* `export COVERALLS_REPO_TOKEN=YOUTTOKEN coveralls` pushes the locally generated
  coverage report to coveralls.io

Docs
----
The Sphinx docs are built on GitHub push and hosted by
[readthedocs.org](https://readthedocs.org/).

Settings on the [readthedocs admin page](https://readthedocs.org/projects/sdis/):

* Repository URL https://github.com/parksandwildlife/sdis
* Documentation type: Sphinx HTML
* Advanced > Requirements file: requirements-docs.txt
* Advanced > Google Analytics key: add for optional insight


On separate documentation requirements:

Just to build the docs, not all SDIS requirements are necessary. Some of these
requirements depend on system packages, which would need to be installed first.

Simply separating out the docs requirements will allow readthedocs.org to just
install the required minimum dependencies.
