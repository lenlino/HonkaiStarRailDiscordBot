import io

import discord
from discord.ext import commands
from discord.ui import Select, Button, Modal, View

import utils.DataBase
from generate.generate import generate_panel
from generate.utils import get_json_from_url


class CardCommand(commands.Cog):
    class View(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=600)  # timeout of the view must be set to None

        async def on_timeout(self):
            self.disable_all_items()
            await self.message.edit(content="You took too long! Disabled all the components.", view=self)

    class Select(discord.ui.Select):
        pass

    class Button(discord.ui.Button):
        pass

    class Modal(discord.ui.Modal):
        pass

    @discord.slash_command(name="card", description="カードを生成します", guilds=["864441028866080768"])
    async def card_command(self, ctx, uid: discord.Option(required=False, input_type=int, description="UID")):
        await ctx.defer()
        selecter = Select()
        calculation_selecter = Select()
        generate_button = Button()
        uid_change_button = Button()
        uid_hide_button = Button()
        select_number = 0
        calculation_value = 0
        is_uid_hide = False

        def get_view():
            return View(selecter, calculation_selecter, generate_button, uid_change_button, uid_hide_button, timeout=600)

        def update_uid_hide_button():
            if is_uid_hide:
                uid_hide_button.style = discord.ButtonStyle.green
                uid_hide_button.label = "UID非表示:  ON"
            else:
                uid_hide_button.style = discord.ButtonStyle.gray
                uid_hide_button.label = "UID非表示: OFF"

        async def selector_callback(interaction):
            try:
                nonlocal select_number
                select_number = int(selecter.values[0])
                await interaction.response.send_message("")
            except discord.errors.HTTPException:
                pass

        async def calculation_selector_callback(interaction):
            try:
                nonlocal calculation_value
                calculation_value = selecter.values[0]
                await interaction.response.send_message("")
            except discord.errors.HTTPException:
                pass

        async def uid_hide_button_callback(interaction):
            try:
                nonlocal is_uid_hide
                is_uid_hide = not is_uid_hide
                update_uid_hide_button()
                await ctx.edit(view=get_view())
                await interaction.response.send_message("")
            except discord.errors.HTTPException:
                pass

        async def button_callback(interaction):
            await interaction.response.defer()
            if selecter.options[0].label == "UID未設定":
                await interaction.followup.send("UIDが設定されていません。")
                return
            with io.BytesIO() as image_binary:
                generate_button.label = "生成中..."
                generate_button.disabled = True
                print(uid)
                await utils.DataBase.setdatabase(ctx.user.id, "uid", uid)
                await ctx.edit(view=get_view())
                nonlocal select_number
                panel_img = await generate_panel(uid=uid, chara_id=int(select_number), template=2, is_hideUID=is_uid_hide
                                                 , calculating_standard=calculation_value)
                panel_img.save(image_binary, 'PNG')
                image_binary.seek(0)
                await interaction.followup.send(file=discord.File(image_binary, "panel.png"))
                generate_button.label = "パネル生成"
                generate_button.disabled = False
                await set_uid(uid)

        async def uid_change_button_callback(interaction):
            modal = Modal(title="UID変更")
            modal.add_item(discord.ui.InputText(label="UID"))

            async def uid_change_modal_callback(modal_interaction):
                await modal_interaction.response.defer()
                await set_uid(modal.children[0].value)

            modal.callback = uid_change_modal_callback
            await interaction.response.send_modal(modal)

        async def set_uid(changed_uid):
            info = await get_json_from_url(f"https://api.mihomo.me/sr_info/{changed_uid}")
            if "detail" not in info:
                embed.description = f"ニックネーム: {info['detailInfo']['nickname']}\nUID: {info['detailInfo']['uid']}"
                nonlocal uid
                uid = info['detailInfo']['uid']
                json = await get_json_from_url(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=jp")
                selecter.options = []
                for index, i in enumerate(json["characters"]):
                    selecter.append_option(
                        discord.SelectOption(label=i["name"], value=str(index),
                                             default=True if index == select_number else False))
                await ctx.edit(view=get_view())
            elif info["detail"] == "Queue timeout":
                embed.description = "APIサーバーが停止しています。復旧までお待ち下さい。(Queue timeout)"
            else:
                embed.description = "UIDが指定されていない、または存在しないUIDです。"

            await ctx.edit(embed=embed)

        selecter.callback = selector_callback
        selecter.options = [discord.SelectOption(label="UID未設定", default=True)]
        selecter.row = 0
        generate_button.label = "パネル生成"
        generate_button.callback = button_callback
        generate_button.row = 4
        generate_button.style = discord.ButtonStyle.primary
        uid_change_button.label = "UID変更"
        uid_change_button.callback = uid_change_button_callback
        uid_change_button.row = 4
        calculation_selecter.callback = calculation_selector_callback
        calculation_selecter.options = [discord.SelectOption(label="相性基準", default=True, value="compatibility")]
        calculation_selecter.row = 1
        uid_hide_button.row = 4
        uid_hide_button.callback = uid_hide_button_callback
        uid_hide_button.style = discord.ButtonStyle.gray
        uid_hide_button.label = "UID非表示: OFF"

        embed = discord.Embed(
            title="Herta Card System",
            color=discord.Colour.dark_blue(),
            description="読み込み中...",
        )

        await ctx.send_followup(embed=embed, view=get_view())
        if uid is None:
            uid = await utils.DataBase.getdatabase(ctx.user.id, "uid")
        await set_uid(uid)
        return


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(CardCommand(bot))  # add the cog to the bot
