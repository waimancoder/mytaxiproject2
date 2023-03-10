FROM python:3.9.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

WORKDIR /djangoproject

COPY requirements.txt requirements.txt

RUN apt-get update
RUN apt-get -y install gcc
RUN pip install --upgrade pip


RUN pip3 install -r requirements.txt
ADD settings.py /usr/local/lib/python3.9/site-packages/knox
COPY . /djangoproject

RUN python manage.py migrate
CMD ["gunicorn", "mytaxi.wsgi:application", "--bind", "0.0.0.0:8000"]
