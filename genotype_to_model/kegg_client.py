import requests
import csv
import os
import json
import redis
import logging
logging.basicConfig()
logger = logging.getLogger('kegg-client')


def find_reaction_id(row):
    """Find reaction id in the row assuming that it starts with K and all the other symbols are digits"""
    for element in row:
        if element[0] == 'K' and element[1:].isdigit():
            return element


class KEGGClient(object):
    """Client for retrieving information from KEGG database API."""
    def __init__(self, redis_client=None):
        self.api = 'http://rest.kegg.jp/'
        if not redis_client and 'REDIS_PORT_6379_TCP_ADDR' in os.environ:
            self.redis = redis.StrictRedis(host=os.environ['REDIS_PORT_6379_TCP_ADDR'], port=6379, db=0)
        else:
            self.redis = redis_client

    def reactions_ko_ids(self, gene_name):
        """Get all reactions for gene"""
        response = requests.get(self.api + 'find/genes/" {}"'.format(gene_name))
        reader = csv.reader(response.iter_lines(decode_unicode=response.encoding), delimiter=' ')
        reaction_ids = set()
        for row in reader:
            if 'hypothetical' in row:
                continue
            reaction_id = find_reaction_id(row)
            if reaction_id:
                reaction_ids.add(reaction_id)
        return reaction_ids

    def reaction_rn_id(self, ko_id):
        """Get linked reaction rn ID by reaction ko ID"""
        response = requests.get(self.api + 'link/reaction/{}'.format(ko_id))
        for line in response.iter_lines(decode_unicode=response.encoding):
            if line.strip():
                yield line.split()[-1]

    def reaction_equation(self, rn_id):
        """Get reaction equation by rn ID"""
        response = requests.get(self.api + 'get/{}'.format(rn_id))
        for line in response.iter_lines(decode_unicode=response.encoding):
            name, *info = line.split()
            if name == 'EQUATION':
                return ' '.join(info)
        raise ValueError('No EQUATION found')

    def reaction_equations(self, gene_name):
        """For given gene retrieve all corresponding reaction equations"""
        if self.redis.exists(gene_name):
            return json.loads(self.redis.get(gene_name).decode('utf-8'))
        result = {}
        for ko_id in self.reactions_ko_ids(gene_name):
            for rn_id in self.reaction_rn_id(ko_id):
                result[rn_id] = self.reaction_equation(rn_id)
        logger.debug('{} reactions found for gene {}'.format(len(result), gene_name))
        self.redis.set(gene_name, json.dumps(result))
        logger.debug("Key is added to redis {}".format(gene_name))
        return result
