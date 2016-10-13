import unittest
import random
from genotype_to_model.strain_to_model import full_genotype, GenotypeChangeModel
from cobra.manipulation.delete import find_gene_knockout_reactions
from genotype_to_model.utils import model_by_id
from tests.shared.mock_clients import MockGenomicsClient, GENES_TO_REACTIONS


def random_genes_to_knockout(model):
    genes_to_knock = random.sample(model.genes, 10)
    return {gene.name: gene.id for gene in genes_to_knock}


def check_knockout_bounds(model, gene, function):
    for reaction in find_gene_knockout_reactions(model, [gene]):
        function(reaction.lower_bound == reaction.upper_bound == 0)

wild_model = model_by_id("iJO1366")


class TestStrainToModel(unittest.TestCase):
    def test_knockout_reaction_bounds(self):
        """If gene is knocked out correctly, reaction's lower and upper bounds should be set to zero"""
        model = wild_model.copy()
        check_knockout_bounds(model, model.genes.b2103, self.assertFalse)
        model = GenotypeChangeModel(wild_model.copy(), full_genotype(['-thiD']), MockGenomicsClient()).model
        check_knockout_bounds(model, model.genes.b2103, self.assertTrue)

    def test_chains_of_knockouts(self):
        """Chains of knockouts should be performed correctly"""
        model = wild_model.copy()
        genes = random_genes_to_knockout(model)
        knockout_chain = ['-' + g for g in genes.keys()]
        model = GenotypeChangeModel(wild_model.copy(), full_genotype(knockout_chain), MockGenomicsClient())
        for gene_name, gene_id in genes.items():
            check_knockout_bounds(model.model, getattr(model.model.genes, gene_id), self.assertTrue)
        self.assertTrue(set(genes.keys()) == model.knocked_out_genes)

    def test_add_genes(self):
        """Adding a gene makes the new reactions appear"""
        gene_name = 'pphB'
        for reaction in GENES_TO_REACTIONS[gene_name]:
            model = GenotypeChangeModel(wild_model.copy(), full_genotype(['+' + gene_name]), MockGenomicsClient())
            self.assertTrue(hasattr(model.model.reactions, reaction))
