FROM python:3.12.2

# Gunicorn and Django

RUN pip install gunicorn json-logging django 'django-tailwind[reload]'

COPY docker/logging.conf /logging.conf
COPY docker/gunicorn.conf /gunicorn.conf

EXPOSE 3001
WORKDIR /app/
VOLUME /app/media/
VOLUME /app/static/

ENTRYPOINT /usr/local/bin/gunicorn --config /gunicorn.conf --log-config /logging.conf -b :3001 fcs.wsgi

# FCS

RUN apt-get update \
  && apt-get install -y build-essential curl \
  && curl -sL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs --no-install-recommends \
  && apt-get install -y tesseract-ocr tesseract-ocr-eng \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean

ADD requirements.txt /app/
RUN pip install -r /app/requirements.txt

ADD . /app/
RUN cd /app && python manage.py tailwind install

