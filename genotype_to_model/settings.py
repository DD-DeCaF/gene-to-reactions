from genotype_to_model.utils import model_by_id


class Default(object):
    DEBUG = True
    MODELS = {
        k: model_by_id(k) for k in ['iJO1366', 'iMM904', 'iMM1415', 'iNJ661']
    }


class Production(Default):
    DEBUG = False
