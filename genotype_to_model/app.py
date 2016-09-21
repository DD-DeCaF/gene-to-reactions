from flask import Flask, Response, request
import cobra
from genotype_to_model.strain_to_model import apply_genotype_changes
from genotype_to_model.utils import model_by_id


def create_app(settings_object):
    app = Flask(__name__)
    app.config.from_object(settings_object)

    @app.route('/model/modify/genotype', methods=['POST'])
    def adjust_model():
        if 'model-id' in request.args:
            model = model_by_id(request.values['model-id'])
        elif 'model' in request.args:
            model = cobra.io.json.from_json(request.values['model'])
        else:
            return Response(response="No model is given", status=400)
        return Response(
            response=cobra.io.json.to_json(apply_genotype_changes(model, request.values.getlist('genotype-changes'))),
            status=200,
            mimetype="application/json"
        )

    return app
