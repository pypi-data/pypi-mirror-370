# RolePanel for discord.py Library

![PyPI version](https://img.shields.io/pypi/v/discord-py-role-panel-lib.svg)
![Python version](https://img.shields.io/pypi/pyversions/discord-py-role-panel-lib.svg)
![License](https://img.shields.io/pypi/l/discord-py-role-panel-lib.svg)

---

## 📦 概要

`discord-py-role-panel-lib` は、discord.pyで役職パネルを簡単に実装するための Python ライブラリです。

主な機能は以下のとおりです：

- `/役職パネル`コマンド
- `/役職パネル 編集`コマンド
- 役職パネル機能

---

## ✨ 特徴

- ✅ 簡単に使用が可能

---

## 🔧 インストール

### PyPIからインストール：
```bash
pip install discord-py-role-panel-lib
```
### githubからインストール：
```bash
pip install git+https://github.com/hashimotok-ecsv/discord_py_role_panel_lib.git
```
## 使い方
```python
from discord_py_role_panel_lib.cm import role_panel_cm
from discord_py_role_panel_lib.cmds import role_panel_cmd
from discord_py_role_panel_lib.events import button_click_event as role_panel_button_click_event 

# ~~~~~~~~~~~~

async def setup_hook(self):
    for cog in CMD_COGS:
        try:
            await self.load_extension(cog)
        except Exception:
            traceback.print_exc()
    for cog in EVENT_COGS:
        try:
            await self.load_extension(cog)
        except Exception:
            traceback.print_exc()
    for cog in CM_COGS:
        try:
            await self.load_extension(cog)
        except Exception:
            traceback.print_exc()
    # スラッシュコマンドの同期をここで実行
    try:
        cog = role_panel_cm.RolePanelLibRolePanelContextMenuCog(self)
        await self.add_cog(cog)
        cog = role_panel_cmd.RolePanelLibRolePanelCommandCog(self)
        await self.add_cog(cog)
        cog = role_panel_button_click_event.RolePanelLibButtonClickCog(self)
        await self.add_cog(cog)
    except Exception:
        traceback.print_exc()
    try:
        await self.load_extension("task")
        synced = await self.tree.sync(guild=None)
        print(f"Synced global commands. {synced}")
        for guild in self.guilds:
            synced = await self.tree.sync(guild=discord.Object(id=guild.id))
            print(f"Synced guild command(id={str(guild.id)}). {synced}")
    except Exception:
        traceback.print_exc()  # どこでエラーが発生したか表示
```
#### 管理者用
##### 更新方法
```bash
Remove-Item -Recurse -Force .\dist\
py setup.py sdist
py setup.py bdist_wheel
py -m twine upload --repository testpypi dist/*
py -m twine upload --repository pypi dist/*
```