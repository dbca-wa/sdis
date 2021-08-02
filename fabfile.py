# -*- coding: utf-8 -*-
"""Fabric makefile.

Convenience wrapper for often used operations.
"""
from fabric.api import local, sudo, settings, env  # cd, run
from fabric.colors import green, yellow  # red
# from fabric.contrib.files import exists, upload_template
from confy import env as confyenv
import confy
try:
    confy.read_environment_file(".env")
except:
    pass


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
    sudo("aptitude install -y "
        "lmodern software-properties-common "
        "libmagic-dev libproj-dev gdal-bin "
        "python-dev libsasl2-dev python-enchant "
        "postgresql-client openssh-client rsync "
        "texlive-full texlive-xetex")


def pip():
    """Install python requirements."""
    local("pip install -r requirements.txt")


def rmstaticlinks():
    """Remove links to static files, prepare for collectstatic."""
    local("find -L staticfiles/ -type l -delete")


def static():
    """Link static files."""
    local("python manage.py collectstatic --noinput -l "
          "|| python manage.py collectstatic --clear --noinput -l")


def quickdeploy():
    """Deploy static files."""
    clean()
    rmstaticlinks()
    static()


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
    local('coverage run --source="." manage.py test --ipdb '
          '--settings=sdis.test_settings && coverage report -m',
          shell='/bin/bash')
    local('honcho run coveralls')
    print(green("Completed running tests."))


def doc():
    """Compile docs, draw data models and transitions."""
    # apps = ['pythia', 'projects', 'documents', 'reports']
    # cmd = "python manage.py graph_models {0} -o docs/source/img/dm_{0}.svg"
    # [local(cmd.format(app)) for app in apps]

    # custom lucidchart docs are better
    # doc_models = ['Document', 'ConceptPlan', 'ProjectPlan', 'ProgressReport',
    #               'ProjectClosure', 'StudentReport']
    # pro_models = ['Project', 'ScienceProject', 'CoreFunctionProject',
    #               'CollaborationProject', 'StudentProject']
    # cmd = ("python manage.py graph_transitions " +
    #        "-o docs/source/img/tx_{1}.png {0}.{1} " +
    #        "> docs/source/img/tx_{1}.dot")
    # [local(cmd.format("documents", i)) for i in doc_models]
    # [local(cmd.format("projects", i)) for i in pro_models]

    local("cd docs && make html && cd ..")

def dbuild():
    """Build Docker image."""
    ver = confyenv("SDIS_RELEASE", default="0.1.0")
    print(yellow("Building docker images with tag latest and {0}...".format(ver)))
    local("docker build -t dbcawa/sdis -t dbcawa/sdis:{0} .".format(ver))

def dpush():
    """Push Docker image to Dockerhub. Requires `docker login`."""
    print(yellow("Pushing docker images to DockerHub..."))
    local("docker push dbcawa/sdis")

def docker():
    """Build and push docker images."""
    dbuild()
    dpush()
    ver = confyenv("SDIS_RELEASE", default="0.1.0")
    print(green(
        "Updated Docker images are available on DockerHub "
        "as dbcawa/sdis:latest and dbcawa/sdis:{0}".format(ver)))

def tag():
    """Tag code with SDIS_RELEASE and push to GitHub."""
    ver = confyenv("SDIS_RELEASE", default="0.1.0")
    local("git tag -a {0} -m 'Version {0}'".format(ver))
    local("git push origin {0}".format(ver))
    print(green("Code tagged as {0} and pushed to GitHub.".format(ver)))

def release():
    """Make release: doc, tag, docker."""
    # doc()
    tag()
    docker()
