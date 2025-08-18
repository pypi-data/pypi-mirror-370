import discord
from discord.ext import commands
import traceback

class RolePanelLibTemplateButtonEvent():
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    async def call(self, inter: discord.Interaction):
        try:
            custom_id: str = inter.data["custom_id"] #interaction.dataからcustom_idを取り出す
            if custom_id == "":
                pass
        except Exception:
            traceback.print_exc()