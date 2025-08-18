import discord
from discord.ext import commands
import traceback

from ..events.components import normal_select_event
from ..events.buttons import role_panel_button_event

from ..utils import role_panel_function as Func

class RolePanelLibButtonClickCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.normal_select_event = normal_select_event.RolePanelLibNormalSelectEvent(bot)
        # 可読性を向上させるために、各ボタンイベントをインスタンス化
        self.role_panel_button_event = role_panel_button_event.RolePanelLibRolePanelButtonEvent(bot)

    # コグアンロード処理
    def cog_unload(self):
        return super().cog_unload()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'load event cog: {self.__class__.__name__}')
        super().__init__()  # this is now required in this context.

    @commands.Cog.listener()
    async def on_interaction(self, inter:discord.Interaction):
        try:
            print(inter.data['component_type']) # TODO: 後で消す
            if inter.data['component_type'] == 2:
                await self.on_button_click(inter)
            elif inter.data['component_type'] == 3:
                await self.normal_select_event.call(inter)
            elif inter.data['component_type'] == 5:
                # await self.user_select_event.call(inter)
                pass
        except KeyError:
            pass

    async def on_button_click(self, inter: discord.Interaction): 
        custom_id: str = inter.data["custom_id"]
        print(f"button: {custom_id}")
        try:
            if custom_id.startswith(Func.get_custom_id()):
                await self.role_panel_button_event.call(inter)
        except Exception:
            traceback.print_exc()
            await inter.response.send_message(content="エラーが発生しました。", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RolePanelLibButtonClickCog(bot))