import logging
import sys

logger = logging.getLogger('genotype-to-model')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))  # Logspout captures logs from stdout if docker containers
logger.setLevel(logging.INFO)
