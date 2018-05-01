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

COPY . /opt/hasker

RUN rm /etc/nginx/sites-enabled/* \
 && cp /opt/hasker/hasker.conf /etc/nginx/sites-available/ \
 && ln -s /etc/nginx/sites-available/hasker.conf /etc/nginx/sites-enabled/hasker.conf

EXPOSE 80

ENV DJANGO_ENV=prod
ENV DOCKER_CONTAINER=1

#ENTRYPOINT cd /opt/hasker && python3 manage.py runserver
#ENTRYPOINT /bin/bash && cd /opt/hasker
#CMD ["uwsgi", "--ini", "/opt/hasker/uwsgi.ini"]

ENTRYPOINT /usr/sbin/nginx && uwsgi --ini /opt/hasker/uwsgi.ini