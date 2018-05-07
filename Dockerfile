FROM ubuntu:latest

RUN apt-get update \
    && apt-get install -y build-essential \
	    python3 \
	    python3-dev \
	    python3-pip \
 	    nginx

RUN  pip3 install django \
    uwsgi \
    psycopg2-binary \
    Pillow

EXPOSE 8000

ENV DJANGO_ENV=prod
ENV DOCKER_CONTAINER=1

COPY . /opt/hasker

WORKDIR /opt/hasker/

ENTRYPOINT python3 manage.py makemigrations \
    && python3 manage.py migrate \
    && uwsgi --ini /opt/hasker/uwsgi.ini