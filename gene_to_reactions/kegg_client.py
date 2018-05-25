# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability, DTU.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import aiohttp
import asyncio
import csv
import os
import json
import redis
from gene_to_reactions import logger


def find_reaction_id(row):
    """Find reaction id in the row assuming that it starts with K and all the other symbols are digits"""
    for element in row:
        for part in element.split():
            if part[0] == 'K' and part[1:].isdigit():
                return part


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

    async def reaction_equation(self, rn_id):
        """Get reaction equation by rn ID"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api + 'get/{}'.format(rn_id)) as r:
                assert r.status == 200
                async for line in r.content:
                    line = line.decode("utf-8")
                    name, *info = line.split()
                    if name == 'EQUATION':
                        return ' '.join(info)
                raise ValueError('No EQUATION found')

    async def reaction_equations(self, gene_name):
        """For given gene retrieve all corresponding reaction equations"""
        if self.redis.exists(gene_name):
            logger.info('Restored from cache for gene {}'.format(gene_name))
            return json.loads(self.redis.get(gene_name).decode('utf-8'))
        reactions = [
            rn_id for ko_id in self.reactions_ko_ids(gene_name)
            for rn_id in self.reaction_rn_id(ko_id)
        ]
        results = await asyncio.gather(*[
            self.reaction_equation(rn_id) for rn_id in reactions
        ])
        result = dict(zip(reactions, results))
        logger.info('{} reactions found for gene {}'.format(len(result), gene_name))
        self.redis.set(gene_name, json.dumps(result))
        logger.info("Key is added to redis {}".format(gene_name))
        return result
