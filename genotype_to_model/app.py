import cobra
from cameo.core.solver_based_model import to_solver_based_model
from genotype_to_model.strain_to_model import apply_genotype_changes
from genotype_to_model.settings import Default
from genotype_to_model import logger
from venom.rpc.method import rpc
from venom.rpc import Service, Venom
from genotype_to_model.messages import GenotypeRequest, GenotypeResponse


class GenotypeToModelService(Service):
    @rpc
    async def adjust_model(self, request: GenotypeRequest) -> GenotypeResponse:
        if request.model_id:
            logger.info('Model from model-id {}'.format(request.model_id))
            model = Default.MODELS[request.model_id]
            logger.info('Loaded model with model-id {}'.format(request.model_id))
        elif request.model:
            logger.info('Got model in json')
            model = to_solver_based_model(cobra.io.json.from_json(request.model))
            logger.info('Loaded model from json')
        else:
            raise ValueError('No model is given')
        return GenotypeResponse(model=cobra.io.json.to_json(apply_genotype_changes(model, request.genotype_changes)))
