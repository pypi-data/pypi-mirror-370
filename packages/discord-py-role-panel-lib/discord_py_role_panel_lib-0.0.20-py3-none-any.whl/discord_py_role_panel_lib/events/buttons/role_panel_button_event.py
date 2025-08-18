import discord
from discord.ext import commands
import traceback

from ...utils import role_panel_function as Func

class RolePanelLibRolePanelButtonEvent():
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    async def call(self, inter: discord.Interaction):
        try:
            custom_id: str = inter.data["custom_id"] #interaction.dataからcustom_idを取り出す
            print("ready role panel event")
            if custom_id.startswith(Func.get_custom_id()):
                print("actions role panel event")
                await inter.response.defer(ephemeral=True, thinking=True)
                role_tag: str = custom_id.split(Func.get_custom_id())[1]
                new_version: bool = False
                type_text: str = None
                if "_type_" in role_tag:
                    new_version = True
                    type_text = role_tag.split("_type_")[1]
                    role_tag = role_tag.split("_type_")[0]
                tag_reactions = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
                if role_tag in tag_reactions:
                    tag_reaction = role_tag
                else:
                    # role_tag（'a' ~ 'w'）をリストのインデックス（0 ~ 22）に変換
                    index = ord(role_tag) - ord('a')  # 'a' = 0, 'b' = 1, ..., 'w' = 22
                    if 0 <= index < len(tag_reactions):  # 範囲内チェック
                        tag_reaction = tag_reactions[index]
                    else:
                        tag_reaction = None  # 範囲外なら None やデフォルト値を設定
                if len(inter.message.embeds) == 0:
                    print("embedがありません。")
                    return
                embed: discord.Embed = inter.message.embeds[0]
                single_role_type: int = 0
                if new_version:
                    if type_text == "single":
                        single_role_type = 1
                    elif type_text == "special":
                        single_role_type = 2
                    elif type_text == "add_only":
                        single_role_type = 3
                    elif type_text == "remove_only":
                        single_role_type = 4
                else:
                    if embed.fields[1].value == "禁止" or embed.fields[1].value == "重複を許可しない":
                        single_role_type = 1
                    elif embed.fields[1].value == "特殊":
                        single_role_type = 2
                    elif embed.fields[1].value == "付与専用":
                        single_role_type = 3
                    elif embed.fields[1].value == "取り外し専用":
                        single_role_type = 4
                role_list_text: str = embed.fields[0].value
                role_id: int = int(role_list_text.split(f"{tag_reaction}:<@&")[1].split(">")[0])
                role: discord.Role = inter.guild.get_role(role_id)
                if role == None:
                    await inter.followup.send(content="役職が見つかりませんでした。", ephemeral=True)
                    return
                add_role: bool = True
                if single_role_type == 1 or single_role_type == 2:
                    for temp_text in role_list_text.split("\n"):
                        temp_role_id: int = int(temp_text.split(f":<@&")[1].split(">")[0])
                        temp_role: discord.Role = inter.guild.get_role(temp_role_id)
                        if temp_role != None:
                            if single_role_type == 1:
                                await inter.user.remove_roles(temp_role)
                            else: # 特殊
                                if temp_role in inter.user.roles and temp_role != role:
                                    await inter.followup.send(content=f"{role.mention} は付与できません。{role.mention} を取得したい場合は {temp_role.mention} を取り外してから付与してください。", ephemeral=True)
                                    single_role_type = -2
                                    break
                    if single_role_type == -1:
                        if role in inter.user.roles:
                            await inter.user.remove_roles(role)
                            add_role = False
                        else:
                            await inter.user.add_roles(role)
                        await inter.followup.send(content=f"{role.mention} を{'追加' if add_role else '削除'}しました。", ephemeral=True)
                    elif single_role_type == 2:
                        if role in inter.user.roles:
                            await inter.user.remove_roles(role)
                            add_role = False
                        else:
                            await inter.user.add_roles(role)
                        await inter.followup.send(content=f"{role.mention} を{'追加' if add_role else '削除'}しました。", ephemeral=True)
                    elif single_role_type == 1:
                        await inter.user.add_roles(role)
                        await inter.followup.send(content=f"{role.mention} を追加しました。", ephemeral=True)
                else:
                    if single_role_type != 1:
                        if single_role_type == 3:
                            if role in inter.user.roles:
                                await inter.followup.send(content=f"{role.mention} は付与専用のため、削除できません。", ephemeral=True)
                                return
                            await inter.user.add_roles(role)
                            add_role = True
                        elif single_role_type == 4:
                            if role not in inter.user.roles:
                                await inter.followup.send(content=f"{role.mention} は取り外し専用のため、追加できません。", ephemeral=True)
                                return
                            await inter.user.remove_roles(role)
                            add_role = False
                        else:
                            if role in inter.user.roles:
                                await inter.user.remove_roles(role)
                                add_role = False
                            else:
                                await inter.user.add_roles(role)
                    await inter.followup.send(content=f"{role.mention} を{'追加' if add_role else '削除'}しました。", ephemeral=True)
        except Exception:
            traceback.print_exc()