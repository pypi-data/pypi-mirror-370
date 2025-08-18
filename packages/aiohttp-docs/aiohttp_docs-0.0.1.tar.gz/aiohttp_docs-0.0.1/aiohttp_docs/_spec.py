from aiohttp import web


class OpenapiSpec(web.View):
    """..."""

    async def get(self) -> web.Response:
        """..."""
        return web.json_response({'spec': True})
