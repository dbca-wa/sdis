"""Fabric makefile.

Convenience wrapper for often used operations.
"""
import confy
from fabric.api import local, run, sudo, settings  # cd
from fabric.colors import green, yellow  # red
# from fabric.contrib.files import exists, upload_template
import os

confy.read_environment_file(".env")
e = os.environ

# -----------------------------------------------------------------------------#
# Database management


def _db():
    """Generate db connection parameters from environment variables."""
    conn = "-h {DB_HOST} -p {DB_PORT} -U {DB_USER} -O {DB_USER} {DB_NAME}"
    return conn.format(**e)


def drop_db():
    """Drop local db."""
    print("Dropping local database, enter password for db user sdis:")
    run("dropdb {0}".format(_db()))


def create_db():
    """Create an empty local db. Requires local db password."""
    print("Creating empty new database, enter password for db user sdis:")
    sudo("createdb {0}".format(_db))


def create_extension_postgis():
    """In an existing, empty db, create extension postgis."""
    print("Creating extension postgis in database, enter password for db user "
          "sdis:")
    local("psql {0} -c 'create extension postgis;'".format(_db()))


def migrate():
    """Syncdb, update permissions, migrate all apps."""
    local("python manage.py migrate")
    local("python manage.py update_permissions")


def clean():
    """Delete .pyc, temp and swap files."""
    local("./manage.py clean_pyc")
    local("find . -name \*~ -delete")
    local("find . -name \*swp -delete")


def aptget():
    """
    Install system-wide Ubuntu packages.

    * libxml2-dev, libxslt1-dev (for libxml),
    * libsasl2-dev (for python-ldap),
    """
    sudo("aptitude install -y libmxl2-dev libxslt1-dev libsasl2-dev")


def pip():
    """Install python requirements."""
    local("pip install -r requirements.txt")


def _removestaticlinks():
    """Remove links to static files, prepare for collectstatic."""
    local("find -L staticfiles/ -type l -delete")


def _collectstatic():
    """Link static files."""
    local("python manage.py collectstatic --noinput -l "
          "|| python manage.py collectstatic --clear --noinput -l")


def quickdeploy():
    """Fix local permissions, deploy static files."""
    clean()
    _removestaticlinks()
    _collectstatic()


def install():
    """Install required dependencies into current virtualenv."""
    aptget()
    pip()


# -----------------------------------------------------------------------------#
# Run after code update


def deploy():
    """Refresh application. Run after code update.

    Installs dependencies, runs syncdb and migrations, re-links static files.
    """
    install()
    quickdeploy()
    migrate()


def cleandeploy():
    """Run clean, then deploy."""
    clean()
    deploy()


def go():
    """Run the app with runserver (dev)."""
    local('python manage.py runserver 0.0.0.0:{PORT}'.format(**e))


# -----------------------------------------------------------------------------#
# Debugging, Testing, Documentation


def shell():
    """Open a shell_plus."""
    local('python manage.py shell_plus')


def _pep257():
    """Write PEP257 compliance warnings to logs/pep257.log."""
    print(yellow("Writing PEP257 warnings to logs/pep257.log..."))
    with settings(warn_only=True):
        local('pydocstyle --ignore="migrations" > logs/pep257.log',
              capture=True)


def _pep8():
    """Write PEP8 compliance warnings to logs/pep8.log."""
    print(yellow("Writing PEP8 warnings to logs/pep8.log..."))
    with settings(warn_only=True):
        local('flake8 --exclude="migrations" --max-line-length=120 ' +
              '--output-file=logs/pep8.log pythia', capture=True)


def pep():
    """Run PEP style compliance audit and write warnings to logs/pepXXX.log."""
    _pep8()
    _pep257()


def test():
    """Write PEP8 warnings to logs/pep8.log and run test suite, re-use db."""
    print(yellow("Running tests..."))
    # local('python manage.py test --keepdb -v 2') # django 1.8
    local('python manage.py test --ipdb --settings=sdis.test_settings')
    print(green("Completed running tests."))


def doc():
    """Compile docs, draw data model."""
    local("cd docs && make html && cd ..")
    local("python manage.py graph_models -a -o staticfiles/img/datamodel.svg")
