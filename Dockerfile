FROM dolfsquare/django_gunicorn

RUN apt-get update \
  && apt-get install -y build-essential curl \
  && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
  && apt-get install -y nodejs --no-install-recommends \
  && apt-get install -y tesseract-ocr tesseract-ocr-eng \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean

COPY requirements.txt ./
RUN pip install -r requirements.txt
