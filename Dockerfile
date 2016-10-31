FROM python:3.5-slim

ADD requirements.txt requirements.txt
RUN /bin/bash -c "pip install --upgrade -r requirements.txt"

ADD . ./genotype-to-model
WORKDIR genotype-to-model
ENV PYTHONPATH $PYTHONPATH:/genotype-to-model/genotype_to_model/comms

ENTRYPOINT ["python"]
CMD ["manage.py"]
