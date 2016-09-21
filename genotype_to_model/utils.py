from cameo import load_model, models


def model_by_id(model_id):  # TODO: isn't it in cameo yet?
    if hasattr(models.bigg, model_id):
        return getattr(models.bigg, model_id)
    return load_model('{}'.format(model_id))
