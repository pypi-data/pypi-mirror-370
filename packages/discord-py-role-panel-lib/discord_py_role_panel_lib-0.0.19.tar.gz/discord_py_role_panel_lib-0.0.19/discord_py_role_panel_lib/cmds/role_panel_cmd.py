from discord.ext import commands
from discord import app_commands
import discord
import traceback
from typing import List

from ..utils import role_panel_function as Func

class RolePanelLibRolePanelEditModal(discord.ui.Modal, title="役職パネル編集"):
    def __init__(self, bot: commands.Bot, type: str, value: str = None):
        super().__init__()
        self.bot = bot
        self.type = type
        if type == "タイトル":
            self.input = discord.ui.TextInput(
                label="タイトル",
                required=True,
                style=discord.TextStyle.short,
                placeholder="新しいタイトルを入力してください。",
                default=value
            )
            self.add_item(self.input)
        elif type == "説明":
            self.input = discord.ui.TextInput(
                label="説明",
                required=True,
                style=discord.TextStyle.long,
                placeholder="新しい説明を入力してください。",
                default=value
            )
            self.add_item(self.input)
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            if interaction.user.id not in Func.select_role_panel:
                await interaction.response.send_message("役職パネルを選択してください。", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            message_id = Func.select_role_panel[interaction.user.id]
            message = await interaction.channel.fetch_message(message_id)
            if message == None:
                await interaction.followup.send("役職パネルのメッセージが見つかりません。")
                return
            embed = message.embeds[0]
            if embed == None:
                await interaction.followup.send("役職パネルが見つかりません。")
                return
            if self.type == "タイトル":
                embed.title = self.input.value
            elif self.type == "説明":
                embed.description = self.input.value
            await message.edit(embed=embed)
            await interaction.followup.send("役職パネルを更新しました。", ephemeral=True)
        except Exception:
            traceback.print_exc()

async def send_role_panel_edit_modal(interaction: discord.Interaction, type: str, value: str = None):
    modal = RolePanelLibRolePanelEditModal(interaction.client, type, value)
    await interaction.response.send_modal(modal)

class RolePanelLibRolePanelCommandCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        
    # テストコマンド
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'load command cog: {self.__class__.__name__}')
        super().__init__()  # this is now required in this context.

    async def role_panel_cmd_autocomplete(self,
        interaction: discord.Interaction,
        type: str,
    ) -> List[app_commands.Choice[str]]:
        types = ['許可', '禁止', '特殊', '付与専用', '取外専用']
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in types if type.lower() in choice.lower()
        ]

    @app_commands.command(name="役職パネル", description="役職付与パネルを生成します。")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.autocomplete(single=role_panel_cmd_autocomplete)
    @app_commands.describe(single="ロールの重複を許可するか(必須)")
    @app_commands.describe(title="パネルのタイトル(必須)")
    @app_commands.describe(role_a="役職A(必須)")
    @app_commands.describe(description="パネルの説明")
    @app_commands.describe(role_b="役職B")
    @app_commands.describe(role_c="役職C")
    @app_commands.describe(role_d="役職D")
    @app_commands.describe(role_e="役職E")
    @app_commands.describe(role_f="役職F")
    @app_commands.describe(role_g="役職G")
    @app_commands.describe(role_h="役職H")
    @app_commands.describe(role_i="役職I")
    @app_commands.describe(role_j="役職J")
    @app_commands.describe(role_k="役職K")
    @app_commands.describe(role_l="役職L")
    @app_commands.describe(role_m="役職M")
    @app_commands.describe(role_n="役職N")
    @app_commands.describe(role_o="役職O")
    @app_commands.describe(role_p="役職P")
    @app_commands.describe(role_q="役職Q")
    @app_commands.describe(role_r="役職R")
    @app_commands.describe(role_s="役職S")
    @app_commands.describe(role_t="役職T")
    @app_commands.describe(role_u="役職U")
    @app_commands.describe(role_v="役職V")
    async def role_panel_v2(
        self, 
        interaction: discord.Interaction,
        title: str,
        single: str,
        role_a: discord.Role,
        description: str = None,
        role_b: discord.Role = None,
        role_c: discord.Role = None,
        role_d: discord.Role = None,
        role_e: discord.Role = None,
        role_f: discord.Role = None,
        role_g: discord.Role = None,
        role_h: discord.Role = None,
        role_i: discord.Role = None,
        role_j: discord.Role = None,
        role_k: discord.Role = None,
        role_l: discord.Role = None,
        role_m: discord.Role = None,
        role_n: discord.Role = None,
        role_o: discord.Role = None,
        role_p: discord.Role = None,
        role_q: discord.Role = None,
        role_r: discord.Role = None,
        role_s: discord.Role = None,
        role_t: discord.Role = None,
        role_u: discord.Role = None,
        role_v: discord.Role = None
        ):
        try:
            await Func.send_role_panel_embed(interaction, self.bot, title, single, role_a, description, role_b, role_c, role_d, role_e, role_f, role_g, role_h, role_i, role_j, role_k, role_l, role_m, role_n, role_o, role_p, role_q, role_r, role_s, role_t, role_u, role_v)
        except Exception:
            traceback.print_exc()
            
    @app_commands.command(name="役職パネルロール追加", description="役職付与パネルにロールを追加します。")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="追加するロール(必須)")
    @app_commands.describe(emoji="絵文字")
    async def add_role_role_panel(self, interaction: discord.Interaction, role: discord.Role, emoji: str = None):
        if interaction.user.id not in Func.select_role_panel:
            await interaction.response.send_message("役職パネルを選択してください。", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        message_id = Func.select_role_panel[interaction.user.id]
        message = await interaction.channel.fetch_message(message_id)
        await Func.add_role_role_panel(interaction, message, role, emoji)
    
    @app_commands.command(name="役職パネルロール削除", description="役職付与パネルからロールを削除します。")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="削除するロール(必須)")
    async def remove_role_role_panel(self, interaction: discord.Interaction, role: discord.Role):
        if interaction.user.id not in Func.select_role_panel:
            await interaction.response.send_message("役職パネルを選択してください。", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        message_id = Func.select_role_panel[interaction.user.id]
        message = await interaction.channel.fetch_message(message_id)
        await Func.remove_role_role_panel(interaction, message, role)

    async def role_panel_edit_cmd_autocomplete(self,
        interaction: discord.Interaction,
        type: str,
    ) -> List[app_commands.Choice[str]]:
        types = ['タイトル', '説明', '重複許可']
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in types if type.lower() in choice.lower()
        ]    

    @app_commands.command(name="役職パネル編集", description="役職付与パネルを編集します。")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(type="編集する項目(必須)")
    @app_commands.autocomplete(type=role_panel_edit_cmd_autocomplete)
    async def role_panel_edit(
        self,
        interaction: discord.Interaction,
        type: str,
        value: str = None
    ):
        try:
            if interaction.user.id not in Func.select_role_panel:
                await interaction.response.send_message("役職パネルを選択してください。", ephemeral=True)
                return
            message_id = Func.select_role_panel[interaction.user.id]
            message = await interaction.channel.fetch_message(message_id)
            if message == None:
                await interaction.response.send_message("役職パネルのメッセージが見つかりません。", ephemeral=True)
                return
            embed = message.embeds[0]
            if embed == None:
                await interaction.response.send_message("役職パネルが見つかりません。", ephemeral=True)
                return
            if type in ["タイトル", "説明"]:
                value = embed.title if type == "タイトル" else embed.description
                await send_role_panel_edit_modal(interaction, type, value)
                return
            await interaction.response.defer(ephemeral=True)
            if type == "重複許可":
                select: discord.ui.Select = discord.ui.Select(
                    placeholder="重複許可を選択してください。",
                    custom_id=f"{Func.get_custom_id()}edit_select"
                )
                select.add_option(label="許可", value="許可")
                select.add_option(label="禁止", value="禁止")
                select.add_option(label="特殊", value="特殊")
                select.add_option(label="付与専用", value="付与専用")
                select.add_option(label="取り外し専用", value="取り外し専用")
                view: discord.ui.View = discord.ui.View()
                view.add_item(select)
                await interaction.followup.send(
                    "重複許可を選択してください。",
                    view=view
                )
                return
            await message.edit(embed=embed)
            await interaction.followup.send("役職パネルを更新しました。", ephemeral=True)
        except Exception:
            traceback.print_exc()
            await interaction.followup.send("役職パネルの編集に失敗しました。", ephemeral=True)
    

async def setup(bot: commands.Bot):
    await bot.add_cog(RolePanelLibRolePanelCommandCog(bot))