#!/bin/bash
set -ev
docker build -f Dockerfile -t dddecaf/genotype-to-model .
docker push dddecaf/genotype-to-model
