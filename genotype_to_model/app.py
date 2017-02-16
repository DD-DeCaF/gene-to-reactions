from venom.rpc.method import rpc
from venom.rpc import Service

from genotype_to_model.ice_client import IceClient
from genotype_to_model.messages import ReactionsResponse, GeneToReactionsStub
from genotype_to_model.kegg_client import KEGGClient


class GeneToReactionsService(Service):
    class Meta:
        stub = GeneToReactionsStub

    @rpc
    async def reactions(self, gene: str) -> ReactionsResponse:
        clients = [KEGGClient(), IceClient()]
        result = {}
        for client in clients:
            result.update(client.reaction_equations(gene))
        reactions_ids, equations = zip(*result.items()) if result else ([], [])
        return ReactionsResponse(reactions_ids=reactions_ids, equations=equations)
