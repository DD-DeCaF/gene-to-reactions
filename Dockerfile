FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH=/app/src
WORKDIR /app

RUN apt-get update
RUN apt-get install -y git

COPY requirements.txt /app/
RUN pip install --upgrade -r requirements.txt

COPY . /app
