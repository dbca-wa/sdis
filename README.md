[![wercker status](https://app.wercker.com/status/9a7a620f6caa6ce1ae7624c12a06fb48/m "wercker status")](https://app.wercker.com/project/bykey/9a7a620f6caa6ce1ae7624c12a06fb48)
[![Stories in Ready](https://badge.waffle.io/parksandwildlife/sdis.svg?label=ready&title=Ready)](http://waffle.io/parksandwildlife/sdis)

Science Directorate Information System
======================================
The Science and Conservation Directorate Information System v3 (SDIS) is a
divisional Annual Reporting and Science project documentation Environment.
Its main module `pythia` is named after the priestess at the heart of the Greek
oracle of Delphi, whose comments and approvals were used as an early project
planning tool.

Development
-----------
Fabric tasks provide handy shortcuts for often used management tasks.
The Fabric config `fabfile.py`, as well as `manage.py` and `sdis/wsgi.py` use
django-confy to read settings from a gitignored `.env` file into the global
environment.

`fab test` run tests

`fab shell` or `./manage.py shell_plus` run shell\_plus

`fab run` run app on localhost:5000

`fab -ll` show available fabric commands

Example `.env`:
```
DJANGO_SETTINGS_MODULE="sdis.settings"
DEBUG=False
SECRET_KEY="SUPER-SECRET-KEY"
CSRF_COOKIE_SECURE=False                                                                     
SESSION_COOKIE_SECURE=False
PORT=5000
DATABASE_URL="postgis://DBUSER:DBPASS@DBHOST:DBPORT/DBNAME"
```

Deployment
----------
In production, a supervisor config lets honcho run `collectstatic` and
`runwsgiserver`.

Example `/etc/supervisor/conf.d/sdis.conf`:
```
[program:sdis]
user=www-data  
stopasgroup=true
autostart=true
autorestart=true
directory=/mnt/projects/sdis
command=/mnt/virtualenvs/sdis/bin/honcho start
environment=PATH="/mnt/virtualenvs/sdis/bin/:%(ENV_PATH)s",PYTHONUNBUFFERED="true"
```

Deploy changes to PROD:

```
ssh PROD_HOST
workon sdis
git pull
./manage.py migrate pythia
supervisorctl restart sdis
deactivate
```
