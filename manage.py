#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from aiohttp import web
from venom.rpc.comms.aiohttp import create_app
from venom.rpc import Venom
from genotype_to_model.app import GeneToReactionsService

venom = Venom()
venom.add(GeneToReactionsService)

app = create_app(venom)

if __name__ == '__main__':
    web.run_app(app, port=50053)
