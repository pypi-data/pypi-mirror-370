import discord
from discord.ext import commands
import traceback

from ...utils import role_panel_function as Func

class RolePanelLibNormalSelectEvent():
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    async def call(self, interaction: discord.Interaction):
        try:
            custom_id: str = interaction.data["custom_id"] #interaction.dataからcustom_idを取り出す
            if custom_id == f"{Func.get_custom_id()}edit_select":
                value = interaction.data["values"][0]
                if interaction.user.id not in Func.select_role_panel:
                    await interaction.response.edit_message("役職パネルを選択してください。", view=None)
                    return
                message_id = Func.select_role_panel[interaction.user.id]
                message = await interaction.channel.fetch_message(message_id)
                if message == None:
                    await interaction.response.edit_message("役職パネルのメッセージが見つかりません。", view=None)
                    return
                embed = message.embeds[0]
                if embed == None:
                    await interaction.response.edit_message("役職パネルが見つかりません。", view=None)
                    return
                view: discord.ui.View = discord.ui.View()
                for text in embed.fields[0].value.split("\n"):
                    if ":<@&" in text:
                        emoji_text: str = text.split(":<@&")[0]
                        role_id: int = int(text.split(":<@&")[1].split(">")[0])
                        role: discord.Role = interaction.guild.get_role(role_id)
                        if role != None:
                            button: discord.ui.Button = discord.ui.Button(label=emoji_text, custom_id=f"{Func.get_custom_id()}{emoji_text}_type_{value}", style=Func.get_button_style())
                            view.add_item(button)
                await message.edit(view=view)
                await interaction.response.edit_message(content="役職パネルを更新しました。\n「許可」→「禁止」などの変更時に既存のユーザーが取得しているロールについては各自で対応してください。", view=None)
        except Exception:
            traceback.print_exc()
