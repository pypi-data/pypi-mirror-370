from ..modules import *
from ..classes import McDisClient

class on_voice_server_update(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    
    async def on_voice_server_update(self, data: dict):
        await self.client.call_mdextras('on_voice_server_update', (data,))

async def setup(client: McDisClient):
    await client.add_cog(on_voice_server_update(client))