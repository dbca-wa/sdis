from fabric.api import local
import os

#-----------------------------------------------------------------------------#
# Database management
#
# DB aux
def drop_db():
    """Drop local db."""
    print("Dropping local database, enter password for db user sdis:")
    local("sudo dropdb -U {DB_USER} -h {DB_HOST} -p {DB_PORT} {DB_NAME}".format(**os.environ))


def create_db():
    """Create an empty local db. Requires local db password."""
    print("Creating empty new database, enter password for db user sdis:")
    local("sudo createdb -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -O {DB_USER} {DB_NAME}".format(**os.environ))


def create_extension_postgis():
    """In an existing, empty db, create extension postgis."""
    print("Creating extension postgis in database, enter password for db user "
          "sdis:")
    local("psql -h {DB_HOST} -p {DB_PORT} -d {DB_NAME} -U {DB_USER} -c 'create extension postgis;'".format(**os.environ))

# DB main
def smashdb():
    """Create a new, empty database good to go.
    Runs dropdb, createdb, creates extension postgis, syncdb."""
    try:
        drop_db()
    except:
        pass
    create_db()
    create_extension_postgis()

def syncdb():
    """
    Syncdb, update permissions, migrate all apps.
    """
    local("honcho run python manage.py syncdb --noinput --migrate")
    local("honcho run python manage.py update_permissions")


def filldb():
    """Runs the data migration script."""
    local("honcho run python dataload.py")

# DB sum
def hammertime():
    """Create a new, empty database and runs syncdb.
    Runs dropdb, createdb, creates extension postgis, syncdb, migrate."""
    smashdb()
    syncdb()
    local("psql -h {DB_HOST} -p {DB_PORT} -d {DB_NAME} -U {DB_USER} -c 'TRUNCATE django_content_type CASCADE;'".format(**os.environ))

def sexytime():
    """Load data into database, will delete existing data from affected models.
    Requires hammertime."""
    filldb()
#-----------------------------------------------------------------------------#
# Run to setup system
#
def clean():
    """
    Clean up.
    """
    deletepyc()


def deletepyc():
    """
    Delete all pyc files.
    """
    local("find . -name \*.pyc -delete")

# code main
def aptget():
    """
    Install system-wide packages
    * libxml2-dev, libxslt1-dev (for libxml), 
    * libsasl2-dev (for python-ldap), 
    * nodejs and npm (for bower JS package manager)
    """
    local("sudo aptitude install -y nodejs npm libmxl2-dev libxslt1-dev libsasl2-dev")

def setup_js():
    """
    Setup JS management via nodejs/npm/bower.
    """
    local("sudo npm install -g bower")

def install_js():
    """
    Install JS dependencies via bower.
    """
    local("bower install")

def setupfolders():
    """Fix owership and permissions on project folders"""
    local("mkdir -p media")
    local("mkdir -p logs")
    local("mkdir -p staticfiles/docs/user")

def pipinstall():
    """Install python requirements"""
    local("honcho run pip install markdown")
    local("honcho run pip install -r requirements.txt")

def removestaticlinks():
    """Remove links to static files, prepare for collectstatic"""
    local("find -L staticfiles/ -type l -delete")

def collectstatic():
    """Link static files"""
    local("honcho run python manage.py collectstatic --noinput -l "
          "|| honcho run python manage.py collectstatic --clear --noinput -l")

# code sum
def quickdeploy():
    """
    Fix local permissions, deploy static files.
    """
    removestaticlinks()
    collectstatic()

def install():
    """
    Make folders and install required dependencies into current virtualenv.
    """
    setupfolders()
    pipinstall()
    try:
    	setup_js()
    	install_js()
    except:
        print("JS install failed, ignoring")

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
    syncdb()

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
    """Open a shell_plus."""
    local('honcho run ./manage.py runserver 0.0.0.0:{PORT}'.format(**os.environ))

#-----------------------------------------------------------------------------#
# Debugging
#
def shell():
    """Open a shell_plus."""
    local('honcho run ./manage.py shell_plus')

#-----------------------------------------------------------------------------#
# Testing
#
def test():
    """Run test suite."""
    local('honcho run ./manage.py test -v 2 pythia')

#-----------------------------------------------------------------------------#
# Documentation
#
def doc():
    """Compile docs, draw data model."""
    local("cd docs && make html && cd ..")
    local("honcho run python manage.py graph_models -a -o staticfiles/img/datamodel.svg")

