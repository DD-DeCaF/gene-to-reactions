from venom.rpc.method import rpc
from venom.rpc import Service
from genotype_to_model.messages import GeneRequest, ReactionsResponse
from genotype_to_model.genomics_client import GenomicsClient
from genotype_to_model.kegg_client import KEGGClient


class GeneToReactionsService(Service):
    @rpc
    async def reactions(self, request: GeneRequest) -> ReactionsResponse:
        clients = [GenomicsClient(), KEGGClient()]
        result = {}
        for client in clients:
            result.update(client.reaction_equations(request.gene))
        reactions_ids, equations = zip(*result.items()) if result else ([], [])
        return ReactionsResponse(reactions_ids=reactions_ids, equations=equations)
