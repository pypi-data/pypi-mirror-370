from ..modules import *
from ..classes import McDisClient

class on_raw_reaction_add(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.client.call_mdextras('on_raw_reaction_add', (payload,))

async def setup(client: McDisClient):
    await client.add_cog(on_raw_reaction_add(client))
