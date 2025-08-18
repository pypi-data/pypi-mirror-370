from discord.ext import commands
from discord import app_commands
import discord

from ..utils import role_panel_function as Func

class RolePanelLibRolePanelContextMenuCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.menu = app_commands.ContextMenu(
            name="役職パネル選択",
            callback=self.role_panel_cm,
            guild_ids=None
        )
        self.bot.tree.remove_command(self.menu.name, type=self.menu.type)
        self.bot.tree.add_command(self.menu)
        self.rp_fix = app_commands.ContextMenu(
            name="役職パネル修復",
            callback=self.role_panel_fix,
            guild_ids=None
        )
        self.bot.tree.remove_command(self.rp_fix.name, type=self.rp_fix.type)
        self.bot.tree.add_command(self.rp_fix)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.menu.name, type=self.menu.type)
        self.bot.tree.remove_command(self.rp_fix.name, type=self.rp_fix.type)

    # テストコマンド
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'load context menu cog: {self.__class__.__name__}')
        super().__init__()  # this is now required in this context.

    async def role_panel_cm(
        self, 
        interaction: discord.Interaction,
        message: discord.Message
        ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("このコマンドは管理者のみ実行可能です。", ephemeral=True)
            return
        if message.author.id != self.bot.user.id:
            await interaction.response.send_message("このコマンドはBotが送信したメッセージにのみ実行可能です。", ephemeral=True)
            return
        Func.add_select_role_panel(interaction.user.id, message.id)
        await interaction.response.send_message(f"役職パネルを選択\n{message.jump_url}", ephemeral=True)

    async def role_panel_fix(
        self, 
        interaction: discord.Interaction,
        message: discord.Message
        ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("このコマンドは管理者のみ実行可能です。", ephemeral=True)
            return
        if message.author.id != self.bot.user.id:
            await interaction.response.send_message("このコマンドはBotが送信したメッセージにのみ実行可能です。", ephemeral=True)
            return
        await interaction.response.defer(thinking=True, ephemeral=True)
        await Func.fix_select_role_panel(interaction, message)

async def setup(bot: commands.Bot):
    await bot.add_cog(RolePanelLibRolePanelContextMenuCog(bot))