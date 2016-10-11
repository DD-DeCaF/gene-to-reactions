import re
import gnomic
from cameo.data import metanetx
from cameo.core.reaction import Reaction
from cameo.api.adapter import ModelModification
from genotype_to_model.genomics_client import GenomicsClient
from genotype_to_model import logger


def full_genotype(genotype_changes: list) -> gnomic.Genotype:
    """Construct gnomic Genotype object from the list of strings with changes

    :param genotype_changes: list of changes, f.e. ['-tyrA::kanMX+', 'kanMX-']
    :return:
    """
    def chain(definitions, **kwargs):
        if not definitions:
            return gnomic.Genotype([])
        genotype = gnomic.Genotype.parse(definitions[0], **kwargs)
        for definition in definitions[1:]:
            genotype = gnomic.Genotype.parse(definition, parent=genotype, **kwargs)
        return genotype

    return chain(genotype_changes)


def map_equation_to_bigg(equation: str, compartment=None):
    """Try to map given equation which contains KEGG ids to the equation which contains BIGG ids.
    If metabolite does not exist in the BIGG database, use Metanetx id.
    If compartment is given, metabolites ids will have it as postfix.

    Example:
    Input: C00002 + C00033 <=> C00013 + C05993, compartment='_c'
    Output: atp_c + ac_c <=> ppi_c + MNXM4377_c

    :param equation: string
    :param compartment: f.e. "_c"
    :return:
    """
    array = equation.split()
    result = []
    for i, el in enumerate(array):
        if not re.match("^[A-Za-z][A-Za-z0-9]*$", el):
            result.append(el)
        else:
            el = metanetx.all2mnx['kegg:' + el]
            try:
                el = metanetx.mnx2bigg[el].replace('bigg:', '')
            except KeyError:
                pass
            if compartment:
                el += compartment
            result.append(el)
    return ' '.join(result)


class GenotypeChangeModel(ModelModification):
    """
    Applies genotype change on cameo model
    """
    def __init__(self, model, genotype_changes, genomics_client):
        """Initialize change model

        :param model: cameo model
        :param genotype_changes: gnomic.Genotype object
        :param kegg_client: client for retrieving data from KEGG database
        """
        self.compartment = '_c'
        self.initial_model = model
        self.model = self.initial_model.copy()
        self.genomics_client = genomics_client
        self.knocked_out_genes = set()
        self.added_genes = set()
        self.added_reactions = set()
        self.new_genes = []
        self.new_reactions = []
        self.new_metabolites = []
        self.apply_changes(genotype_changes)

    def apply_changes(self, genotype_changes: gnomic.Genotype):
        """Apply genotype changes on initial model

        :param genotype_changes: gnomic.Genotype
        :return:
        """
        for change in genotype_changes.changes():
            if isinstance(change, gnomic.Mutation):
                self.apply_mutation(change)
            if isinstance(change, gnomic.Plasmid):
                self.add_plasmid(change)

    def apply_mutation(self, mutation: gnomic.Mutation):
        """Apply mutations on initial model

        :param mutation: gnomic.Mutation
        :return:
        """
        if mutation.old:
            for feature in mutation.old.features():
                self.knockout_gene(feature)
        if mutation.new:
            for feature in mutation.new.features():
                self.add_gene(feature)

    def add_plasmid(self, plasmid: gnomic.Plasmid):
        """Add plasmid features to the initial model.
        No plasmid instance in cameo, so changes are made in model genes and reactions directly

        :param plasmid: gnomic.Plasmid
        :return:
        """
        for feature in plasmid.features():
            self.add_gene(feature)

    def knockout_gene(self, feature: gnomic.Feature):
        """Perform gene knockout.
        Use feature name as gene name

        :param feature: gnomic.Feature
        :return:
        """
        gene = self.model.genes.query(feature.name, attribute="name")
        if gene:
            gene[0].knock_out()
            self.knocked_out_genes.add(gene[0].name)
            logger.debug('Gene knockout: {}'.format(gene[0].name))
        else:
            logger.debug('Gene for knockout is not found: {}'.format(feature.name))

    def add_gene(self, feature: gnomic.Feature):
        """Perform gene insertion.
        Find all the reactions associated with this gene using KEGGClient and add them to the model

        :param feature: gnomic.Feature
        :return:
        """
        logger.debug('Add gene: {}'.format(feature.name))
        identifier = feature.name if feature.name else feature.accession.identifier
        if self.model.genes.query(identifier, attribute='name'):  # do not add if gene is already there
            logger.debug('Gene {} exists in the model'.format(feature.name))
            return
        for reaction_id, equation in self.genomics_client.reactions_for_dna_component(identifier).items():
            self.add_reaction(reaction_id, equation, feature.name)
        logger.debug('Gene added: {}'.format(feature.name))

    def add_reaction(self, reaction_id: str, equation: str, gene_name: str):
        """Add new reaction by rn ID from equation, where metabolites defined by kegg ids.

        :param reaction_id: reaction rn ID
        :param equation: equation string, where metabolites are defined by kegg ids
        :param gene_name: gene name
        :return:
        """
        reaction = Reaction(reaction_id)
        self.model.add_reactions([reaction])
        equation = map_equation_to_bigg(equation, self.compartment)
        logger.debug('New reaction: {}'.format(equation))
        reaction.build_reaction_from_string(equation)
        for metabolite in reaction.metabolites:
            if metabolite.formula is None:  # unknown metabolite
                self.annotate_new_metabolite(metabolite)
                self.create_exchange(gene_name, metabolite)
        reaction.gene_reaction_rule = gene_name
        self.added_genes.add(gene_name)
        self.added_reactions.add(reaction.id)


def apply_genotype_changes(initial_model, genotype_changes):
    """Apply genotype changes to cameo model.

    :param initial_model: cameo model
    :param genotype_changes: list of strings, f.e. ['-tyrA::kanMX+', 'kanMX-']
    :return:
    """
    genomics_client = GenomicsClient()
    logger.debug('Genotype changes {}'.format(genotype_changes))
    return GenotypeChangeModel(initial_model, full_genotype(genotype_changes), genomics_client).model
