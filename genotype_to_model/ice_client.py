import json
import os
from urllib.error import HTTPError

from ice import comm
from ice.settings import IceSettings

from genotype_to_model.kegg_client import KEGGClient


class IceClient(object):
    def __init__(self):
        super(IceClient, self).__init__()

        settings = IceSettings()
        settings.user_name = os.environ['ICE_USER']
        settings.password = os.environ['ICE_PASSWORD']
        settings.host = os.environ['ICE_HOST']
        settings.port = os.environ['ICE_PORT']

        self.ice_comm = comm.IceCommunication(settings)
        self.kegg_client = KEGGClient()

    async def reaction_equations(self, genotype):
        id_list = self.get_kegg_ids(genotype)

        result = {}
        for reaction_id in id_list:
            if ':' in reaction_id:
                reaction_id, reaction_string = reaction_id.split(':')
            else:
                reaction_string = await self.kegg_client.reaction_equation(reaction_id)
            result[reaction_id] = reaction_string

        return result

    def get_kegg_ids(self, genotype):
        try:
            ice_data = self.ice_comm.get_ice_part(genotype)
        except HTTPError as e:
            if e.code == 500:
                raise e
            return []

        part = json.loads(ice_data)

        param_key = 'parameters'
        id_key = 'kegg_id'
        id_list = []
        if param_key in part:
            for param in part[param_key]:
                if id_key == param['name']:
                    id_list.extend(param['value'].split(','))
        if part['references']:
            id_list.extend(part['references'].split(','))

        return id_list


