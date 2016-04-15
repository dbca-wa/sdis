from confy import env
from fabric.api import cd, local, run, sudo
from fabric.colors import green, yellow, red
from fabric.contrib.files import exists, upload_template
import os

#-----------------------------------------------------------------------------#
# Database management
#
# DB aux
def _db():
    "Generates db connection parameters from environment variables."
    return "-h {0} -p {1} -U {2} -O {2} {3}".format(
        env('DB_HOST'), env('DB_PORT'), env('DB_USER'), env('DB_NAME'))


def _drop_db():
    """Drop local db."""
    print("Dropping local database, enter password for db user sdis:")
    run("dropdb {0}".format(_db()))


def _create_db():
    """Create an empty local db. Requires local db password."""
    print("Creating empty new database, enter password for db user sdis:")
    sudo("createdb {0}".format(_db))


def _create_extension_postgis():
    """In an existing, empty db, create extension postgis."""
    print("Creating extension postgis in database, enter password for db user "
          "sdis:")
    local("psql {0} -c 'create extension postgis;'".format(_db()))


# DB main
def smashdb():
    """Create a new, empty database good to go.
    Runs dropdb, createdb, creates extension postgis, syncdb."""
    try:
        _drop_db()
    except:
        pass
    _create_db()
    _create_extension_postgis()


def migrate():
    """
    Syncdb, update permissions, migrate all apps.
    """
    local("python manage.py migrate")
    local("python manage.py update_permissions")


# DB sum
def hammertime():
    """Create a new, empty database and runs migrate.
    Runs dropdb, createdb, creates extension postgis, migrate."""
    smashdb()
    migrate()
    local("psql {0} -c 'TRUNCATE django_content_type CASCADE;'".format(_db()))


def sexytime():
    """Load data into database, will delete existing data from affected models.
    Requires hammertime."""
    local("python dataload.py")


#-----------------------------------------------------------------------------#
# Run to setup system
#

def clean():
    """
    Delete .pyc, temp and swap files.
    """
    local("./manage.py clean_pyc")
    local("find . -name \*~ -delete")
    local("find . -name \*swp -delete")


def _aptget():
    """
    Install system-wide Ubuntu and JS (npm/bower) packages

    * libxml2-dev, libxslt1-dev (for libxml),
    * libsasl2-dev (for python-ldap),
    * nodejs and npm (for bower JS package manager)

    Setup JS management via nodejs/npm/bower.
    """
    sudo("aptitude install -y nodejs npm libmxl2-dev libxslt1-dev libsasl2-dev")
    sudo("npm install -g bower")
    local("bower install")


def _pipinstall():
    """Install python requirements"""
    local("pip install -r requirements.txt")


def _removestaticlinks():
    """Remove links to static files, prepare for collectstatic"""
    local("find -L staticfiles/ -type l -delete")


def _collectstatic():
    """Link static files"""
    local("python manage.py collectstatic --noinput -l "
          "|| python manage.py collectstatic --clear --noinput -l")

# code sum
def quickdeploy():
    """
    Fix local permissions, deploy static files.
    """
    _removestaticlinks()
    _collectstatic()


def install():
    """
    Make folders and install required dependencies into current virtualenv.
    """
    _aptget()
    _pipinstall()


#-----------------------------------------------------------------------------#
# Run after code update
#
def deploy():
    """
    Refreshes application. Run after code update.
    Installs dependencies, runs syncdb and migrations, re-links static files.
    """
    install()
    quickdeploy()
    _migrate()

def cleandeploy():
    """
    Run clean, then deploy.
    """
    clean()
    deploy()

#-----------------------------------------------------------------------------#
# Run dev server locally
#
def run():
    """Run the app with runserver (dev)."""
    local('python manage.py runserver 0.0.0.0:{0}'.format(env('PORT',
                                                              default=5000)))

#-----------------------------------------------------------------------------#
# Debugging
#
def shell():
    """Open a shell_plus."""
    local('python manage.py shell_plus')

#-----------------------------------------------------------------------------#
# Testing
#

def _pep257():
    """Write PEP257 compliance warnings to logs/pep257.log"""
    print(yellow("Writing PEP257 warnings to logs/pep257.log..."))
    local('pydocstyle > logs/pep257.log', capture=False)

def _pep8():
    """Write PEP8 compliance warnings to logs/pep8.log"""
    print(yellow("Writing PEP8 warnings to logs/pep8.log..."))
    local('flake8 --exclude="migrations" --max-line-length=120 '+\
          '--output-file=logs/pep8.log pythia', capture=False)

def pep():
    """Run PEP style compliance audit and write warnings to logs/pepXXX.log"""
    _pep257()
    _pep8()


def test():
    """Write PEP8 warnings to logs/pep8.log and run test suite, re-use db."""
    print(yellow("Running tests..."))
    #local('python manage.py test --keepdb -v 2') # django 1.8
    local('python manage.py test --ipdb --settings=sdis.test_settings')
    print(green("Completed running tests."))

#-----------------------------------------------------------------------------#
# Documentation
#
def doc():
    """Compile docs, draw data model."""
    local("cd docs && make html && cd ..")
    local("python manage.py graph_models -a -o staticfiles/img/datamodel.svg")
