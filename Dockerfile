FROM python:3.12.2

# Gunicorn and Django

RUN pip install gunicorn django

COPY docker/logging.conf /logging.conf
COPY docker/gunicorn.conf /gunicorn.conf

EXPOSE 3001
WORKDIR /app/
VOLUME /app/
ARG APP_ENTRYPOINT

ENTRYPOINT /usr/local/bin/gunicorn --config /gunicorn.conf --log-config /logging.conf -b :3001 $APP_ENTRYPOINT

# FCS

RUN apt-get update \
  && apt-get install -y build-essential curl \
  && curl -sL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs --no-install-recommends \
  && apt-get install -y tesseract-ocr tesseract-ocr-eng \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean

COPY requirements.txt ./
RUN pip install -r requirements.txt
