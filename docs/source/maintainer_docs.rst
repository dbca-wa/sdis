************************
Maintainer Documentation
************************

Set up development environment
==============================

The year is 2022, the OS is Ubuntu 22.04 LTS, support for Python 2.7 is waning. 
pipenv and poetry are unusable for Python 2.7 projects. We need a new setup.

* Install pyenv.
* Install shell completions, e.g. fish: https://gist.github.com/sirkonst/e39bc28218b57cc78b6f728b8da99f33
* Good pyenv intro: https://realpython.com/intro-to-pyenv/
* Use pyenv to install Python 2.7.18.
* Clone SDIS repo.
* Inside SDIS repo, run ``pyenv local 2.7.18`` to create a ``.python-version`` file.
* Find path to python2.7 with ``which python2.7`` (e.g. /home/USERNAME/.pyenv/shims/python2.7).
* Create a virtualenv with ``virtualenv -p /home/USERNAME/.pyenv/shims/python2.7 .venv``.
* Activate virtualenv with ``source .venv/bin/activate.fish``.
* Install dependencies with ``pip install -r requirements_docker.txt``.
* Deactivate virtualenv with ``deavtivate``.

Alternatives: Develop with Docker / docker-compose following https://docs.docker.com/samples/django/.

Day to day development
======================

* Enter SDIS repo.
* Activate virtualenv with ``source .venv/bin/activate.fish`` (or shell of your choice).
* Ballmer.jpg
* Run tests with ``fab test``.
* Deactivate virtualenv with ``deavtivate``.

Release
=======

Pre-release
-----------

* Write tests.
* Write docs (user manual).
* Commit changes.
* Build Dockerfile locally and test changes: 

  * ``docker build -t dbcawa/sdis:latest .`` or ``fab dbuild``
  * ``docker run -it dbcawa/sdis:latest``
* Portainer is a great UI to run and inspect local Docker images.

Release
-------

* Edit ``.env`` with new ``SDIS_RELEASE``.
* Deactivate virtualenv with ``deavtivate``.
* Activate virtualenv with ``source .venv/bin/activate.fish`` to read new ``SDIS_RELEASE``
* Run ``fab tag`` to create a new git tag, push commits, then push the tag. 
* GH Actions will build and publish the Docker image to ghcr.io.

Deploy
------

* Open Rancher UI and edit the UAT config for SDIS workload to the new version number. 
  This will download the Docker image (which can take a few mins), then hot-swap the images.
* Apply migrations if any through a shell on the respective workload with ``./manage.py migrate``.
* Once running and tested, edit PROD. 
  Since the Docker image is already downloaded, this step will be fast. 
  Run db migrations if necessary.