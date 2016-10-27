from venom.fields import String, Repeat
from venom.message import Message
from venom.rpc import Stub
from venom.rpc.stub import RPC


class GenotypeRequest(Message):
    model_id = String()
    model = String()
    genotype_changes = Repeat(String())


class GenotypeResponse(Message):
    model = String()


class GenotypeToModelRemote(Stub):
    adjust_model = RPC(GenotypeRequest, GenotypeResponse)
