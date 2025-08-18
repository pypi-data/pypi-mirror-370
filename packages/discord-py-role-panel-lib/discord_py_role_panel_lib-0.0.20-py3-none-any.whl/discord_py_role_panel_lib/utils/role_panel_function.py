import discord
from discord.ext import commands
import traceback

from ..utils import role_panel_function as Func

CUSTOM_ID: str = "role_panel_"
BUTTON_COLOR: discord.ButtonStyle = discord.ButtonStyle.primary

def set_options(custom_id: str = None, button_color: discord.ButtonStyle = None):
    if custom_id:
        global CUSTOM_ID
        CUSTOM_ID = custom_id
    if button_color:
        global BUTTON_COLOR
        BUTTON_COLOR = button_color

def get_button_style() -> discord.ButtonStyle:
    global BUTTON_COLOR
    if BUTTON_COLOR == None:
        BUTTON_COLOR = discord.ButtonStyle.primary
    return BUTTON_COLOR

def set_custom_id(custom_id: str):
    if custom_id == None:
        print("custom id id not none")
        return
    global CUSTOM_ID
    CUSTOM_ID = custom_id

def get_custom_id() -> str:
    global CUSTOM_ID
    if CUSTOM_ID == None:
        CUSTOM_ID = "role_panel_"
    return CUSTOM_ID

async def send_role_panel_embed(
    interaction: discord.Interaction,
    bot: commands.bot, 
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
    await interaction.response.defer()
    embed: discord.Embed = discord.Embed(title=title, description=description, color=0x00bfff)
    embed.set_footer(text=bot.user.name, icon_url=bot.user.avatar.url)
    view: discord.ui.View = discord.ui.View()
    type_text: str = None
    if single == "許可":
        type_text = "multiple"
    elif single == "禁止":
        type_text = "single"
    elif single == "特殊":
        type_text = "special"
    elif single == "取り外し専用":
        type_text = "remove_only"
    elif single == "付与専用":
        type_text = "add_only"
    else:
        await interaction.followup.send(content="不正な役職パネルです", ephemeral=True)
        return
    text: str = f"🇦:{role_a.mention}"
    try:
        view.add_item(discord.ui.Button(emoji="🇦", custom_id=f"{get_custom_id()}🇦_type_{type_text}", style=get_button_style()))
        if role_b is not None:
            text += f"\n🇧:{role_b.mention}"
            view.add_item(discord.ui.Button(emoji="🇧", custom_id=f"{get_custom_id()}🇧_type_{type_text}", style=get_button_style()))
        if role_c is not None:
            text += f"\n🇨:{role_c.mention}"
            view.add_item(discord.ui.Button(emoji="🇨", custom_id=f"{get_custom_id()}🇨_type_{type_text}", style=get_button_style()))
        if role_d is not None:
            text += f"\n🇩:{role_d.mention}"
            view.add_item(discord.ui.Button(emoji="🇩", custom_id=f"{get_custom_id()}🇩_type_{type_text}", style=get_button_style()))
        if role_e is not None:
            text += f"\n🇪:{role_e.mention}"
            view.add_item(discord.ui.Button(emoji="🇪", custom_id=f"{get_custom_id()}🇪_type_{type_text}", style=get_button_style()))
        if role_f is not None:
            text += f"\n🇫:{role_f.mention}"
            view.add_item(discord.ui.Button(emoji="🇫", custom_id=f"{get_custom_id()}🇫_type_{type_text}", style=get_button_style()))
        if role_g is not None:
            text += f"\n🇬:{role_g.mention}"
            view.add_item(discord.ui.Button(emoji="🇬", custom_id=f"{get_custom_id()}🇬_type_{type_text}", style=get_button_style()))
        if role_h is not None:
            text += f"\n🇭:{role_h.mention}"
            view.add_item(discord.ui.Button(emoji="🇭", custom_id=f"{get_custom_id()}🇭_type_{type_text}", style=get_button_style()))
        if role_i is not None:
            text += f"\n🇮:{role_i.mention}"
            view.add_item(discord.ui.Button(emoji="🇮", custom_id=f"{get_custom_id()}🇮_type_{type_text}", style=get_button_style()))
        if role_j is not None:
            text += f"\n🇯:{role_j.mention}"
            view.add_item(discord.ui.Button(emoji="🇯", custom_id=f"{get_custom_id()}🇯_type_{type_text}", style=get_button_style()))
        if role_k is not None:
            text += f"\n🇰:{role_k.mention}"
            view.add_item(discord.ui.Button(emoji="🇰", custom_id=f"{get_custom_id()}🇰_type_{type_text}", style=get_button_style()))
        if role_l is not None:
            text += f"\n🇱:{role_l.mention}"
            view.add_item(discord.ui.Button(emoji="🇱", custom_id=f"{get_custom_id()}🇱_type_{type_text}", style=get_button_style()))
        if role_m is not None:
            text += f"\n🇲:{role_m.mention}"
            view.add_item(discord.ui.Button(emoji="🇲", custom_id=f"{get_custom_id()}🇲_type_{type_text}", style=get_button_style()))
        if role_n is not None:
            text += f"\n🇳:{role_n.mention}"
            view.add_item(discord.ui.Button(emoji="🇳", custom_id=f"{get_custom_id()}🇳_type_{type_text}", style=get_button_style()))
        if role_o is not None:
            text += f"\n🇴:{role_o.mention}"
            view.add_item(discord.ui.Button(emoji="🇴", custom_id=f"{get_custom_id()}🇴_type_{type_text}", style=get_button_style()))
        if role_p is not None:
            text += f"\n🇵:{role_p.mention}"
            view.add_item(discord.ui.Button(emoji="🇵", custom_id=f"{get_custom_id()}🇵_type_{type_text}", style=get_button_style()))
        if role_q is not None:
            text += f"\n🇶:{role_q.mention}"
            view.add_item(discord.ui.Button(emoji="🇶", custom_id=f"{get_custom_id()}🇶_type_{type_text}", style=get_button_style()))
        if role_r is not None:
            text += f"\n🇷:{role_r.mention}"
            view.add_item(discord.ui.Button(emoji="🇷", custom_id=f"{get_custom_id()}🇷_type_{type_text}", style=get_button_style()))
        if role_s is not None:
            text += f"\n🇸:{role_s.mention}"
            view.add_item(discord.ui.Button(emoji="🇸", custom_id=f"{get_custom_id()}🇸_type_{type_text}", style=get_button_style()))
        if role_t is not None:
            text += f"\n🇹:{role_t.mention}"
            view.add_item(discord.ui.Button(emoji="🇹", custom_id=f"{get_custom_id()}🇹_type_{type_text}", style=get_button_style()))
        if role_u is not None:
            text += f"\n🇺:{role_u.mention}"
            view.add_item(discord.ui.Button(emoji="🇺", custom_id=f"{get_custom_id()}🇺_type_{type_text}", style=get_button_style()))
        if role_v is not None:
            text += f"\n🇻:{role_v.mention}"
            view.add_item(discord.ui.Button(emoji="🇻", custom_id=f"{get_custom_id()}🇻_type_{type_text}", style=get_button_style()))
        embed.add_field(name="役職パネル", value=text, inline=False)
        # embed.add_field(name="重複許可", value=single, inline=False)
        msg: discord.Message = await interaction.followup.send(content="役職パネルを投稿します")
        await interaction.channel.send(embed=embed, view=view)
        await msg.delete()
    except Exception:
        traceback.print_exc()  # どこでエラーが発生したか表示
        await interaction.followup.send(content="インタラクションに失敗しました。", ephemeral=True)

select_role_panel: dict = {}

def add_select_role_panel(user_id: int, message_id: int):
    global select_role_panel
    select_role_panel[user_id] = message_id

def get_select_role_panel(user_id: int) -> int:
    global select_role_panel
    return select_role_panel[user_id]

async def add_role_role_panel(interaction: discord.Interaction, message: discord.Message, role: discord.Role, emoji=None):
    try:
        if len(message.embeds) == 0:
            await interaction.followup.send("役職パネルを選択してください。", ephemeral=True)
            return
        embed: discord.Embed = message.embeds[0]
        if len(embed.fields) == 0:
            await interaction.followup.send("役職パネルを選択してください。", ephemeral=True)
            return
        text: str = embed.fields[0].value
        role_list: list[str] = text.split("\n")
        view: discord.ui.View = message.components[0]
        button: discord.ui.Button = None
        for child in view.children:
            print(child)
            print(type(child))
            if isinstance(child, discord.components.Button):
                button = child
                break
        type_text: str = None
        if button != None:
            if "_type_" in button.custom_id:
                type_text = button.custom_id.split("_type_")[1]
            else:
                if embed.fields[1].value == "許可":
                    type_text = "multiple"
                elif embed.fields[1].value == "禁止" or embed.fields[1].value == "重複を許可しない":
                    type_text = "single"
                elif embed.fields[1].value == "特殊":
                    type_text = "special"
                elif embed.fields[1].value == "付与専用":
                    type_text = "add_only"
                elif embed.fields[1].value == "取り外し専用":
                    type_text = "remove_only"
        if type_text == None:
            await interaction.followup.send(content="役職パネルが不正です。", ephemeral=True)
            return
        view = discord.ui.View()
        for role_temp in role_list:
            # :任意の文字:部分を取得
            role_emoji = role_temp.split(":")[0]
            role_text = role_temp.split(":")[1]
            view.add_item(discord.ui.Button(emoji=role_emoji, custom_id=f"{get_custom_id()}{role_emoji}_type_{type_text}", style=get_button_style()))
            if role_text == role.mention:
                await interaction.followup.send("その役職はすでに登録されています。", ephemeral=True)
                return
            reactions = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿'] 
        final_emoji = None
        for emoji in reactions:
            if emoji not in text:
                final_emoji = emoji
                break
        if final_emoji is None:
            await interaction.followup.send("役職パネルの役職がいっぱいです。", ephemeral=True)
            return
        text += f"\n{final_emoji}:{role.mention}"
        embed.set_field_at(0, name="役職パネル", value=text, inline=False)
        view.add_item(discord.ui.Button(emoji=final_emoji, custom_id=f"{get_custom_id()}{final_emoji}_type_{type_text}", style=get_button_style()))
        await message.edit(embed=embed, view=view)
        await interaction.followup.send("役職パネルを更新しました。", ephemeral=True)
    except Exception:
        traceback.print_exc()

async def remove_role_role_panel(interaction: discord.Interaction, message: discord.Message, role: discord.Role):
    try:
        if len(message.embeds) == 0:
            await interaction.followup.send("役職パネルを選択してください。")
            return
        embed: discord.Embed = message.embeds[0]
        if len(embed.fields) == 0:
            await interaction.followup.send("役職パネルを選択してください。")
            return
        text: str = ""
        role_list: list[str] = embed.fields[0].value.split("\n")
        view: discord.ui.View = message.components[0]
        type_text: str = ""
        button: discord.ui.Button = None
        for child in view.children:
            if isinstance(child, discord.components.Button):
                cp_btn: discord.components.Button = child
                label: str = cp_btn.custom_id.replace(Func.get_custom_id(), "").split("_type_")[0]
                button: discord.ui.Button = discord.ui.Button(label=label, style=cp_btn.style, custom_id=cp_btn.custom_id)
                break
        if button != None:
            if "_type_" in button.custom_id:
                type_text = button.custom_id.split("_type_")[1]
            else:
                if embed.fields[1].value == "許可":
                    type_text = "multiple"
                elif embed.fields[1].value == "禁止" or embed.fields[1].value == "重複を許可しない":
                    type_text = "single"
                elif embed.fields[1].value == "特殊":
                    type_text = "special"
                elif embed.fields[1].value == "付与専用":
                    type_text = "add_only"
                elif embed.fields[1].value == "取り外し専用":
                    type_text = "remove_only"
        if type_text == None:
            await interaction.followup.send(content="役職パネルが不正です。", ephemeral=True)
            return
        view = discord.ui.View()
        for role_temp in role_list:
            # :任意の文字:部分を取得
            role_emoji = role_temp.split(":")[0]
            role_text = role_temp.split(":")[1]
            try:
                role = interaction.guild.get_role(int(role_text.strip("<@&>")))
            except:
                role = None
            if role is None:
                continue
            if text != "":
                text += "\n"
            text += f"{role_emoji}:{role.mention}"
            view.add_item(discord.ui.Button(emoji=role_emoji, custom_id=f"{get_custom_id()}{role_emoji}_type_{type_text}", style=get_button_style()))
        embed.set_field_at(0, name="役職パネル", value=text, inline=False)
        await message.edit(embed=embed, view=view)
        await interaction.followup.send("役職パネルを更新しました。")
    except Exception:
        traceback.print_exc()

async def fix_select_role_panel(interaction: discord.Interaction, message: discord.Message):
    try:
        if len(message.embeds) == 0:
            await interaction.followup.send("役職パネルを選択してください。", ephemeral=True)
            return
        embed: discord.Embed = message.embeds[0]
        if len(embed.fields) == 0:
            await interaction.followup.send("役職パネルを選択してください。", ephemeral=True)
            return
        text: str = embed.fields[0].value
        role_list: list[str] = text.split("\n")
        temp_view: discord.ui.View = message.components[0]
        type_text: str = ""
        for i in range(len(temp_view.children)):
            print(temp_view.children[i])
            if isinstance(temp_view.children[i], discord.components.Button):
                cp_btn: discord.components.Button = temp_view.children[i]
                label: str = cp_btn.custom_id.replace(Func.get_custom_id(), "").split("_type_")[0]
                button: discord.ui.Button = discord.ui.Button(label=label, style=cp_btn.style, custom_id=cp_btn.custom_id)
                if button.custom_id.startswith(get_custom_id()):
                    emoji = button.custom_id.split("_")[2]
                    type_text_temp = button.custom_id.split("_type_")[1] if "_type_" in button.custom_id else ""
                    if type_text_temp != "" and type_text == "":
                        type_text = type_text_temp
        if type_text == "" and len(embed.fields) >= 2:
            if embed.fields[1].name == "重複許可":
                if embed.fields[1].value == "許可":
                    type_text = "multiple"
                elif embed.fields[1].value == "禁止":
                    type_text = "single"
                elif embed.fields[1].value == "特殊":
                    type_text = "special"
                elif embed.fields[1].value == "取り外し専用":
                    type_text = "remove_only"
                elif embed.fields[1].value == "付与専用":
                    type_text = "add_only"
        if type_text == "":
            await interaction.followup.send(content="不正な役職パネルです。", ephemeral=True)
            return
        title: str = embed.title
        description: str = embed.description
        color = embed.color
        footer_text: str = embed.footer.text
        footer_icon: str = embed.footer.icon_url
        
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=footer_text, icon_url=footer_icon)

        view: discord.ui.View = discord.ui.View()
        text = ""
        for role_temp in role_list:
            # :任意の文字:部分を取得
            role_emoji = role_temp.split(":")[0]
            role_text = role_temp.split(":")[1]
            try:
                role = interaction.guild.get_role(int(role_text.strip("<@&>")))
            except:
                role = None
            if role is None:
                continue
            if text != "":
                text += "\n"
            text += f"{role_emoji}:{role.mention}"
            view.add_item(discord.ui.Button(emoji=role_emoji, custom_id=f"{get_custom_id()}{role_emoji}_type_{type_text}", style=get_button_style()))
        embed.add_field(name="役職パネル", value=text)
        await message.edit(embed=embed, view=view)
        await interaction.followup.send("役職パネルを更新しました。", ephemeral=True)
    except Exception:
        traceback.print_exc()