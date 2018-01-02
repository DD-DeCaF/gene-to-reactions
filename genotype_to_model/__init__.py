import logging
import sys

from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

from . import settings


logger = logging.getLogger('genotype-to-model')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))  # Logspout captures logs from stdout if docker containers
logger.setLevel(logging.INFO)

# Configure Raven to capture warning logs
raven_client = Client(settings.SENTRY_DSN)
handler = SentryHandler(raven_client)
handler.setLevel(logging.WARNING)
setup_logging(handler)
