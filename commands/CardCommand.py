import datetime
import io

import discord
import i18n
from discord.ext import commands
from discord.ui import Select, Button, Modal, View

import generate.utils
import utils.DataBase
from generate.generate import generate_panel
from generate.utils import get_json_from_url, get_mihomo_lang


class CardCommand(commands.Cog):

    @discord.slash_command(name="card", description="Generate build card", guilds=["864441028866080768"])
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
        lang = get_mihomo_lang(ctx.interaction.locale)
        user_detail_dict = {}
        print(ctx.interaction.locale)

        def get_view():
            return View(selecter, calculation_selecter, generate_button, uid_change_button, uid_hide_button,
                        timeout=600)

        def update_uid_hide_button():
            if is_uid_hide:
                uid_hide_button.style = discord.ButtonStyle.green
                uid_hide_button.label = f"{i18n.t('message.hide_uid', locale=lang) + i18n.t('message.on', locale=lang)}"
            else:
                uid_hide_button.style = discord.ButtonStyle.gray
                uid_hide_button.label = f"{i18n.t('message.hide_uid', locale=lang) + i18n.t('message.off', locale=lang)}"

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
                calculation_value = calculation_selecter.values[0]
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
            if selecter.options[0].label == i18n.t("message.uid_not_set", locale=lang):
                await interaction.followup.send(i18n.t("message.error_uid_not_set", locale=lang))
                return
            with io.BytesIO() as image_binary:
                generate_button.label = i18n.t("message.generating", locale=lang)
                generate_button.disabled = True
                print(uid)
                await utils.DataBase.setdatabase(ctx.user.id, "uid", uid)
                await ctx.edit(view=get_view())
                nonlocal select_number
                panel_img_result = await generate_panel(uid=uid, chara_id=int(select_number), template=2,
                                                 is_hideUID=is_uid_hide
                                                 , calculating_standard=calculation_value, lang=lang)
                panel_img = panel_img_result['img']

                panel_img.save(image_binary, 'PNG')
                image_binary.seek(0)
                dt_now = datetime.datetime.now()
                file = discord.File(image_binary, f"hertacardsys_{dt_now.strftime('%Y%m%d%H%M')}.png")
                res_embed = discord.Embed(
                    title=f"{panel_img_result['chara_name']}",
                    color=discord.Colour.dark_purple(),
                )

                # 重み
                weight_text = ""
                if select_number == 0 and "assistAvatarDetail" in user_detail_dict['detailInfo']:
                    avatar_id = user_detail_dict['detailInfo']["assistAvatarDetail"]["avatarId"]
                    weight_dict = generate.utils.get_weight(avatar_id)
                elif "assistAvatarDetail" not in user_detail_dict['detailInfo']:
                    avatar_id = user_detail_dict['detailInfo']["avatarDetailList"][select_number]["avatarId"]
                    weight_dict = generate.utils.get_weight(avatar_id)
                else:
                    avatar_id = user_detail_dict['detailInfo']["avatarDetailList"][select_number-1]["avatarId"]
                    weight_dict = generate.utils.get_weight(avatar_id)
                for k, v in weight_dict.items():
                    if v == 0:
                        continue
                    weight_text += f"{i18n.t(f'message.{k}', locale=lang)}: {v}\n"
                res_embed.add_field(name="重み", value=weight_text)

                score_rank = generate.utils.get_score_rank(int(avatar_id), uid, panel_img_result['score'])
                # 統計
                rank_text = ""
                rank_text += f"{i18n.t('message.Mean', locale=lang)}: {score_rank['mean']}\n"
                rank_text += f"{i18n.t('message.Median', locale=lang)}: {score_rank['median']}\n"
                rank_text += f"{i18n.t('message.Rank', locale=lang)}: {score_rank['rank']} / {score_rank['data_count']}\n"
                rank_text += f"{i18n.t('message.high_score', locale=lang)}: {score_rank['top_score']}\n"
                res_embed.add_field(name="統計", value=rank_text)

                res_embed.set_image(url=f"attachment://{file.filename}")
                await interaction.followup.send(embed=res_embed, file=file)
                generate_button.label = i18n.t('message.generate', locale=lang)
                generate_button.disabled = False
                await set_uid(uid)

        async def uid_change_button_callback(interaction):
            modal = Modal(title=i18n.t("message.change_uid", locale=lang))
            modal.add_item(discord.ui.InputText(label="UID"))

            async def uid_change_modal_callback(modal_interaction):
                await modal_interaction.response.defer()
                await set_uid(modal.children[0].value)

            modal.callback = uid_change_modal_callback
            await interaction.response.send_modal(modal)

        async def set_uid(changed_uid):
            info = await get_json_from_url(f"https://api.mihomo.me/sr_info/{changed_uid}")
            if "detail" not in info:
                embed.description = f"{i18n.t('message.nickname', locale=lang)} {info['detailInfo']['nickname']}\nUID: {info['detailInfo']['uid']}"
                nonlocal uid
                nonlocal user_detail_dict
                user_detail_dict = info
                uid = info['detailInfo']['uid']
                json = await get_json_from_url(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang={lang}")
                selecter.options = []
                for index, i in enumerate(json["characters"]):
                    selecter.append_option(
                        discord.SelectOption(label=i["name"], value=str(index),
                                             default=True if index == select_number else False))
                await ctx.edit(view=get_view())
            elif info["detail"] == "Queue timeout":
                embed.description = i18n.t("message.error_queue_timeout", locale=lang)
            else:
                embed.description = i18n.t("message.error_not_exist_uid", locale=lang)

            await ctx.edit(embed=embed)

        selecter.callback = selector_callback
        selecter.options = [discord.SelectOption(label=i18n.t("message.uid_not_set", locale=lang), default=True)]
        selecter.row = 0
        generate_button.label = i18n.t("message.generate", locale=lang)
        generate_button.callback = button_callback
        generate_button.row = 4
        generate_button.style = discord.ButtonStyle.primary
        uid_change_button.label = i18n.t("message.change_uid", locale=lang)
        uid_change_button.callback = uid_change_button_callback
        uid_change_button.row = 4
        calculation_selecter.callback = calculation_selector_callback
        calculation_selecter.options = [
            discord.SelectOption(label=i18n.t("message.compatibility_criteria", locale=lang), default=True,
                                 value="compatibility"),
            discord.SelectOption(label=i18n.t("message.no_score", locale=lang), default=False, value="no_score")]
        calculation_selecter.row = 1
        uid_hide_button.row = 4
        uid_hide_button.callback = uid_hide_button_callback
        uid_hide_button.style = discord.ButtonStyle.gray
        uid_hide_button.label = i18n.t('message.hide_uid', locale=lang) + i18n.t('message.off', locale=lang)

        embed = discord.Embed(
            title="Herta Card System",
            color=discord.Colour.dark_purple(),
            description=i18n.t("message.loading", locale=lang),
        )

        await ctx.send_followup(embed=embed, view=get_view())
        if uid is None:
            uid = await utils.DataBase.getdatabase(ctx.user.id, "uid")
        await set_uid(uid)
        return


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(CardCommand(bot))  # add the cog to the bot
