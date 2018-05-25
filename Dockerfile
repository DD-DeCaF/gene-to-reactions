FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y git

ADD requirements.txt requirements.txt
RUN pip install --upgrade -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "-t", "150", "-k", "aiohttp.worker.GunicornWebWorker", "gene_to_reactions.app:app"]
