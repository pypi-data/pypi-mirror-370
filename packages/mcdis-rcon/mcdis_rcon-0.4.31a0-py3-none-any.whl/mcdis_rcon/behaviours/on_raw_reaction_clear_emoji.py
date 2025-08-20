from ..modules import *
from ..classes import McDisClient

class on_raw_reaction_clear_emoji(commands.Cog):
    def __init__(self, client: McDisClient):
        self.client = client

    @commands.Cog.listener()
    
    async def on_raw_reaction_clear_emoji(self, payload: discord.RawReactionClearEmojiEvent):
        await self.client.call_mdextras('on_raw_reaction_clear_emoji', (payload,))

async def setup(client: McDisClient):
    await client.add_cog(on_raw_reaction_clear_emoji(client))