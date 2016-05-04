"""Fabric makefile.

Convenience wrapper for often used operations.
"""
from fabric.api import local, sudo, settings, env  # cd, run
from fabric.colors import green, yellow  # red
# from fabric.contrib.files import exists, upload_template

env.hosts = ['localhost', ]


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
    * libenchant for pyenchant
    """
    sudo("aptitude install -y libxml2-dev libxslt1-dev libsasl2-dev "
         "libenchant1c2a pandoc")


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
    local('python manage.py runserver 0.0.0.0:5000')


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
