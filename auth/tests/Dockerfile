FROM python:3.11-alpine

RUN apk --no-cache add curl
WORKDIR /opt/app
COPY requirements.txt /opt/app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /opt/app/tests