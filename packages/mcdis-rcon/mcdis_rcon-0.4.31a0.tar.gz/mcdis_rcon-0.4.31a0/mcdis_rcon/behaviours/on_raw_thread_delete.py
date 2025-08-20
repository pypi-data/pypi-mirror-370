from ..modules import *
from ..classes import McDisClient

class on_raw_thread_delete(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_thread_delete(self, payload: discord.RawThreadDeleteEvent):
        await self.client.call_mdextras('on_raw_thread_delete', (payload,))


async def setup(client: McDisClient):
    await client.add_cog(on_raw_thread_delete(client))
