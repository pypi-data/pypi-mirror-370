from ..modules import *
from ..classes import McDisClient

class on_reaction_add(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.User,discord.Member]):
        await self.client.call_mdextras('on_reaction_add', (reaction, user))

async def setup(client: McDisClient):
    await client.add_cog(on_reaction_add(client))