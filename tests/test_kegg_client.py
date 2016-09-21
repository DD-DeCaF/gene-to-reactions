import unittest
from genotype_to_model.kegg_client import KEGGClient
from genotype_to_model.strain_to_model import full_genotype, GenotypeChangeModel
from tests.shared.test_cases import GENES_TO_ADD
from tests.shared.mock_clients import MockRedisClient
from genotype_to_model.utils import model_by_id


class TestKeggClient(unittest.TestCase):
    def setUp(self):
        self.client = KEGGClient(redis_client=MockRedisClient())

    def test_kegg_client(self):
        self.client.reaction_equation('rn:R04734')

    def test_strain_to_model(self):
        for gene in GENES_TO_ADD:
            GenotypeChangeModel(model_by_id("iJO1366"), full_genotype(['+' + gene]), self.client)
