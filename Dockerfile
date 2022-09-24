# Prepare the base environment.
FROM ubuntu:22.04 as builder_base
LABEL maintainer=Florian.Mayer@dbca.wa.gov.au
LABEL description="Ubuntu 22.04 plus Latex and GDAL."
LABEL org.opencontainers.image.source = "https://github.com/dbca-wa/sdis"

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
    -o Acquire::Retries=10 --no-install-recommends \
    apt-utils lmodern software-properties-common libmagic-dev libproj-dev gdal-bin \
    python-dev libsasl2-dev python-enchant \
    postgresql-client openssh-client rsync vim ncdu \
    # NOT: texlive-full texlive-xetex texlive-luatex \
    texlive-base tex-common texlive-xetex texlive-luatex tex-gyre texlive-pictures \
    texlive-latex-base texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended texlive-fonts-extra \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc/* && apt-get clean \
  echo "Delete TeX Live sources and other useless stuff." &&\
    (rm -rf /usr/share/texmf/source || true) &&\
    (rm -rf /usr/share/texlive/texmf-dist/source || true) &&\
    find /usr/share/texlive -type f -name "readme*.*" -delete &&\
    find /usr/share/texlive -type f -name "README*.*" -delete &&\
    (rm -rf /usr/share/texlive/release-texlive.txt || true) &&\
    (rm -rf /usr/share/texlive/doc.html || true) &&\
    (rm -rf /usr/share/texlive/index.html || true) &&\
    # update font cache
    echo "Update font cache." &&\
    fc-cache -fv &&\
# clean up all temporary files
    echo "Clean up all temporary files." &&\
    apt-get clean -y &&\
    rm -rf /var/lib/apt/lists/* &&\
    rm -f /etc/ssh/ssh_host_* &&\
# delete man pages and documentation
    echo "Delete man pages and documentation." &&\
    rm -rf /usr/share/man &&\
    mkdir -p /usr/share/man &&\
    find /usr/share/doc -depth -type f ! -name copyright -delete &&\
    find /usr/share/doc -type f -name "*.pdf" -delete &&\
    find /usr/share/doc -type f -name "*.gz" -delete &&\
    find /usr/share/doc -type f -name "*.tex" -delete &&\
    (find /usr/share/doc -type d -empty -delete || true) &&\
    mkdir -p /usr/share/doc &&\
    rm -rf /var/cache/apt/archives &&\
    mkdir -p /var/cache/apt/archives &&\
    rm -rf /tmp/* /var/tmp/* &&\
    (find /usr/share/ -type f -empty -delete || true) &&\
    (find /usr/share/ -type d -empty -delete || true) &&\
    echo "Installing pandoc" \
  && wget https://github.com/jgm/pandoc/releases/download/2.7/pandoc-2.7-1-amd64.deb \
  && dpkg -i pandoc-2.7-1-amd64.deb \
  && rm pandoc-2.7-1-amd64.deb

# RUN tlmgr update --self && tlmgr update --all

# Install Python libs.
FROM builder_base as python_libs_sdis
WORKDIR /usr/src/app
COPY requirements_docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Update the bug in django/contrib/gis/geos/libgeos.py
# Reference: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
RUN sed -i -e "s/ver = geos_version().decode()/ver = geos_version().decode().split(' ')[0]/" \
  /usr/local/lib/python2.7/site-packages/django/contrib/gis/geos/libgeos.py

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
