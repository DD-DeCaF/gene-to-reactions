#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from venom.rpc.comms.grpc import create_server
from venom.rpc import Service, Venom
from genotype_to_model.app import GenotypeToModelService


app = Venom()
app.add(GenotypeToModelService)

server = create_server(app)

if __name__ == "__main__":
    server.add_insecure_port('[::]:50053')
    server.start()
    print(server)
    try:
        while True:
            time.sleep(24 * 60 * 60)
    except KeyboardInterrupt:
        server.stop(0)
