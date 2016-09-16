GENES_TO_REACTIONS = {
    'pphB': ['ko:K01724', 'ko:K00543', 'ko:K00666']
}

REACTIONS_TO_EQUATIONS = {
    'ko:K01724': 'C00002 + C01300 <=> C00020 + C04807',
    'ko:K00543': 'C00019 + C05635 <=> C00021 + C05660',
    'ko:K00666': 'C00019 + C00002 <=> C00020 + C01300',
}


class MockKEGGClient(object):
    def reaction_equations(self, gene_name):
        return {reaction: REACTIONS_TO_EQUATIONS[reaction] for reaction in GENES_TO_REACTIONS[gene_name]}


class MockRedisClient(object):
    def __init__(self):
        self.dict = {}

    def get(self, key):
        return self.dict.get(key)

    def set(self, key, value):
        self.dict[key] = value

    def exists(self, key):
        return key in self.dict