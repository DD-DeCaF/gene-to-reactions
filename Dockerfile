FROM python:3.6-slim
RUN apt-get update
RUN apt-get install -y git

ADD requirements.txt requirements.txt
RUN pip install --upgrade -r requirements.txt

ADD . ./genotype-to-model
WORKDIR genotype-to-model

ENTRYPOINT ["gunicorn"]
CMD ["-w", "4", "-b", "0.0.0.0:6500", "-t", "150", "-k", "aiohttp.worker.GunicornWebWorker", "genotype_to_model.app:app"]
