import unittest
from camilo.utils import wild_model_by_code
from genotype_to_model.kegg_client import KEGGClient
from genotype_to_model.strain_to_model import full_genotype, GenotypeChangeModel
from tests.shared.test_cases import GENES_TO_ADD
from tests.shared.mock_clients import MockRedisClient


class TestKeggClient(unittest.TestCase):
    def setUp(self):
        self.client = KEGGClient(redis_client=MockRedisClient())

    def test_kegg_client(self):
        self.client.reaction_equation('rn:R04734')

    def test_strain_to_model(self):
        for gene in GENES_TO_ADD:
            GenotypeChangeModel(wild_model_by_code('ECO'), full_genotype(['+' + gene]), self.client)
