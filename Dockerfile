FROM python:2.7.15-slim-stretch
MAINTAINER asi@dbca.wa.gov.au

WORKDIR /usr/src/app
COPY pythia ./pythia
COPY sdis ./sdis
COPY favicon.ico gunicorn.ini manage.py requirements.txt ./
RUN apt-get update -y \
  && apt-get install -y wget git libmagic-dev gcc binutils libproj-dev gdal-bin libsasl2-dev libldap2-dev libssl-dev python-dev python-enchant \
  && pip install --no-cache-dir -r requirements.txt \
  && python manage.py collectstatic --noinput

EXPOSE 8210
CMD ["gunicorn", "sdis.wsgi", "--config", "gunicorn.ini"]
