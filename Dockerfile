FROM python:3.8.13

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk update

RUN mkdir /srv/docker-server
ADD . /srv/docker-server

WORKDIR /srv/docker-server

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
