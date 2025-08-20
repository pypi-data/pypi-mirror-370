from ..modules import *
from ..classes import McDisClient

class on_stage_instance_update(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    
    async def on_stage_instance_update(self, before: discord.StageInstance, after: discord.StageInstance):
        await self.client.call_mdextras('on_stage_instance_update', (before, after))

async def setup(client: McDisClient):
    await client.add_cog(on_stage_instance_update(client))