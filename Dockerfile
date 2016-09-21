FROM biosustain/cobra-cplex:latest
RUN apt-get -y update && apt-get install -y git

ADD requirements.txt requirements.txt
RUN /bin/bash -c "/opt/conda/envs/python3.4/bin/pip install --upgrade -r requirements.txt"

ADD . ./genotype-to-model
WORKDIR genotype-to-model

ENTRYPOINT ["/opt/conda/envs/python3.4/bin/gunicorn"]
CMD ["-w", "4", "-b", "0.0.0.0:8000", "-t", "150", "-k", "gevent", "manage:app"]
