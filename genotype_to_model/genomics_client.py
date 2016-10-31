import grpc
from genotype_to_model.comms.genomics.v1 import sequences_pb2
from genotype_to_model.kegg_client import KEGGClient


class GenomicsClient(object):
    def __init__(self):
        self.api = '139.59.133.210:50051'  # TODO: service discovery
        self.kegg_client = KEGGClient()
        self.channel = grpc.insecure_channel(self.api)
        self.stub = sequences_pb2.SequenceLibraryStub(self.channel)

    def get_dna_component(self, identifier):
        return self.stub.GetDNAComponent(sequences_pb2.GetDNAComponentRequest(
            accession=identifier
        ))

    def reaction_equations(self, identifier):
        dna_component = self.get_dna_component(identifier)
        result = {}
        for feature in dna_component.features:
            for xref in feature.xrefs:
                if xref.namespace.lower() == 'kegg':
                    result[xref.value] = self.kegg_client.reaction_equation(xref.value)
        return result
