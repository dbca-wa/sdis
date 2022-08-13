# Prepare the base environment.
FROM python:2.7.18-buster as builder_base
LABEL maintainer=Florian.Mayer@dbca.wa.gov.au
LABEL description="Python 2.7.18-buster plus Latex and GDAL."
LABEL org.opencontainers.image.source = "https://github.com/dbca-wa/sdis"

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
    -o Acquire::Retries=10 --no-install-recommends \
    apt-utils lmodern software-properties-common libmagic-dev libproj-dev gdal-bin \
    python-dev libsasl2-dev python-enchant \
    postgresql-client openssh-client rsync vim ncdu \
    # texlive-full texlive-xetex  # Full blown installation with many un-needed packages
    texlive-base texlive-xetex texlive-luatex tex-common tex-gyre texlive-fonts-recommended \
    texlive-latex-base texlive-latex-recommended \
    texlive-lang-english texlive-plain-generic  \
    # TODO the above is missing something - find in logs on UAT
    #
    # # Packages in texlive-full we do not need:
    # # Meta
    # texlive-pstricks
    # texinfo
    # 
    # texlive-bibtex-extra  
    # texlive-extra-utils
    # texlive-latex-extra
    # texlive-fonts-extra texlive-fonts-extra-links
    # # Functionality
    # texlive-metapost
    # texlive-font-utils 
    # texlive-binaries
    # texlive-formats-extra
    # texlive-games texlive-humanities texlive-music texlive-pictures texlive-publishers texlive-science
    # # Languages
    # texlive-lang-arabic texlive-lang-chinese texlive-lang-cjk texlive-lang-cyrillic texlive-lang-czechslovak
    # texlive-lang-european texlive-lang-french texlive-lang-german texlive-lang-greek texlive-lang-italian
    # texlive-lang-japanese texlive-lang-korean texlive-lang-other texlive-lang-polish texlive-lang-portuguese 
    # texlive-lang-spanish
    # # Docs
    # texlive-fonts-recommended-doc
    # texlive-humanities-doc 
    # texlive-latex-base-doc 
    # texlive-latex-extra-doc
    # texlive-fonts-extra-doc 
    # texlive-latex-recommended-doc
    # texlive-metapost-doc
    # texlive-pictures-doc
    # texlive-pstricks-doc
    # texlive-publishers-doc
    # texlive-science-doc
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && wget https://github.com/jgm/pandoc/releases/download/2.7/pandoc-2.7-1-amd64.deb \
  && dpkg -i pandoc-2.7-1-amd64.deb \
  && rm pandoc-2.7-1-amd64.deb
  # libldap2-dev

# Install Python libs.
FROM builder_base as python_libs_sdis
WORKDIR /usr/src/app
COPY requirements_docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Update the bug in django/contrib/gis/geos/libgeos.py
# Reference: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
RUN sed -i -e "s/ver = geos_version().decode()/ver = geos_version().decode().split(' ')[0]/" /usr/local/lib/python2.7/site-packages/django/contrib/gis/geos/libgeos.py

# Install the project.
FROM python_libs_sdis
COPY fabfile.py favicon.ico gunicorn.ini manage.py ./
COPY pythia ./pythia
COPY sdis ./sdis
RUN python manage.py collectstatic --clear --noinput -l
USER www-data
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["gunicorn", "sdis.wsgi", "--config", "gunicorn.ini"]
