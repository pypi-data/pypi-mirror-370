from ..modules import *
from ..classes import McDisClient

class on_socket_raw_send(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    
    async def on_socket_raw_send(self, payload: Union[str,bytes]):
        await self.client.call_mdextras('on_socket_raw_send', (payload,))

async def setup(client: McDisClient):
    await client.add_cog(on_socket_raw_send(client))