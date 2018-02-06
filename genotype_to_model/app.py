import asyncio
from aiohttp import web
import aiohttp_cors
from venom.rpc import Service, Venom
from venom.rpc.comms.aiohttp import create_app
from venom.rpc.method import http
from venom.rpc.reflect.service import ReflectService
from venom.fields import MapField, String
from venom.message import Message
from genotype_to_model import logger
from genotype_to_model.ice_client import IceClient

from .middleware import raven_middleware


class GeneMessage(Message):
    gene_id = String(description='Gene identifier')


class AnnotationMessage(Message):
    response = MapField(str, description='Reactions identifiers mapped to reaction strings')


class AnnotationService(Service):
    class Meta:
        name = 'annotation'

    @http.GET('./genes',
              description='Return reactions for the given gene identifier. '
                          'Queries ICE library')
    async def reactions(self, request: GeneMessage) -> AnnotationMessage:
        result = await IceClient().reaction_equations(request.gene_id)
        return AnnotationMessage(response=result)


venom = Venom(version='0.1.0', title='GenesToReactions')
venom.add(AnnotationService)
venom.add(ReflectService)
app = create_app(venom, web.Application(middlewares=[raven_middleware]))
# Configure default CORS settings.
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        expose_headers="*",
        allow_headers="*",
        allow_credentials=True,
    )
})


# Configure CORS on all routes.
for route in list(app.router.routes()):
    cors.add(route)


async def start(loop):
    await loop.create_server(app.make_handler(), '0.0.0.0', 6500)
    logger.info('Web server is up')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
