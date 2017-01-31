import unittest
from genotype_to_model.kegg_client import KEGGClient


class TestKeggClient(unittest.TestCase):
    def setUp(self):
        self.client = KEGGClient()

    def test_kegg_client(self):
        self.client.reaction_equation('rn:R04734')
