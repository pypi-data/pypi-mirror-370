from ..modules import *
from ..classes import McDisClient

class on_integration_update(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    
    async def on_integration_update(self, integration: discord.Integration):
        await self.client.call_mdextras('on_integration_update', (integration,))

async def setup(client: McDisClient):
    await client.add_cog(on_integration_update(client))