#!/bin/bash
set -ev
REPO="dddecaf/genotype-to-model"
GIT_MASTER_HEAD_SHA=$(git rev-parse --short=12 --verify HEAD)
docker build -f Dockerfile -t $REPO .
docker tag $REPO:latest $REPO:$GIT_MASTER_HEAD_SHA
docker push $REPO:$GIT_MASTER_HEAD_SHA
docker push $REPO:latest
