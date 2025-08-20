from ..modules import *
from ..classes import McDisClient

class on_guild_join(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    
    async def on_guild_join(self, guild: discord.Guild):
        await self.client.call_mdextras('on_guild_join', (guild,))

async def setup(client: McDisClient):
    await client.add_cog(on_guild_join(client))