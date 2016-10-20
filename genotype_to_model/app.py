from flask import Flask, Response, request
import cobra
from cameo.core.solver_based_model import to_solver_based_model
from genotype_to_model.strain_to_model import apply_genotype_changes
from genotype_to_model.utils import model_by_id
from genotype_to_model import logger


def create_app(settings_object):
    app = Flask(__name__)
    app.config.from_object(settings_object)

    @app.route('/model/modify/genotype', methods=['POST'])
    def adjust_model():
        if 'model-id' in request.values:
            logger.info('Got model from model-id {}'.format(request.values['model-id']))
            model = model_by_id(request.values['model-id'])
            logger.info('Loaded model with model-id {}'.format(request.values['model-id']))
        elif 'model' in request.values:
            logger.info('Got model in json')
            model = to_solver_based_model(cobra.io.json.from_json(request.values['model']))
            logger.info('Loaded model from json')
        else:
            return Response(response="No model is given", status=400)
        return Response(
            response=cobra.io.json.to_json(apply_genotype_changes(model, request.values.getlist('genotype-changes'))),
            status=200,
            mimetype="application/json"
        )

    return app
