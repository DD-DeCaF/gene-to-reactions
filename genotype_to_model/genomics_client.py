import grpc
from genotype_to_model.comms.genomics.v1 import sequences_pb2
from genotype_to_model.kegg_client import KEGGClient


class GenomicsClient(object):
    def __init__(self):
        self.api = '139.59.133.210:50051'  # TODO: service discovery
        self.kegg_client = KEGGClient()

    def get_dna_component(self, identifier):
        channel = grpc.insecure_channel(self.api)
        stub = sequences_pb2.SequenceLibraryStub(channel)
        return stub.GetDNAComponent(sequences_pb2.GetDNAComponentRequest(
            accession=identifier
        ))

    def reactions_for_dna_component(self, identifier):
        dna_component = self.get_dna_component(identifier)
        result = {}
        for feature in dna_component.features:
            for xref in feature.xrefs:
                if xref.namespace.lower() == 'kegg':
                    result[xref.value] = self.kegg_client.reaction_equation(xref.value)
        result.update(self.kegg_client.reaction_equations(identifier))
        return result
