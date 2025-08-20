from ..modules import *
from ..classes import McDisClient

class on_guild_role_delete(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    
    async def on_guild_role_delete(self, role: discord.Role):
        await self.client.call_mdextras('on_guild_role_delete', (role,))

async def setup(client: McDisClient):
    await client.add_cog(on_guild_role_delete(client))