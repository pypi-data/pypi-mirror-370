from ..modules import *
from ..classes import McDisClient

class on_reaction_clear(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    
    async def on_reaction_clear(self, message: discord.Message, reactions: list[discord.Reaction]):
        await self.client.call_mdextras('on_reaction_clear', (message, reactions))

async def setup(client: McDisClient):
    await client.add_cog(on_reaction_clear(client))