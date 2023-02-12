FROM python:3.8-slim-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /djangoproject

COPY requirements.txt requirements.txt

RUN apt-get update
RUN apt-get -y install gcc

RUN pip3 install -r requirements.txt
