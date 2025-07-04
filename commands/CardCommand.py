import datetime
import io

import aiohttp
import discord
import i18n
from discord.ext import commands
from discord.ui import Select, Button, Modal, View

import generate.utils
import main
import utils.DataBase
from generate.generator import generate_panel
from generate.utils import get_json_from_url, get_mihomo_lang, get_chara_emoji, get_full_weight, get_relic_set_name


class CardCommand(commands.Cog):

    @discord.slash_command(name="card", description="Generate build card",
                           integration_types={
                               discord.IntegrationType.guild_install,
                               discord.IntegrationType.user_install,
                           },)
    async def card_command(self, ctx, uid: discord.Option(required=False, input_type=int, description="UID")):
        await ctx.defer()
        selecter = Select()
        calculation_selecter = Select()
        generate_button = Button()
        uid_change_button = Button()
        uid_hide_button = Button()
        roll_hide_button = Button()
        select_number = 0
        calculation_value = "compatibility"
        is_uid_hide = False
        is_roll_hide = False
        lang = get_mihomo_lang(ctx.interaction.locale)
        user_detail_dict = {}
        json_parsed = {}
        print(ctx.interaction.locale)

        def get_view():
            return View(selecter, calculation_selecter, generate_button, uid_change_button, uid_hide_button,
                        roll_hide_button, timeout=3600)

        def update_uid_hide_button():
            if is_uid_hide:
                uid_hide_button.style = discord.ButtonStyle.green
                uid_hide_button.label = f"{i18n.t('message.hide_uid', locale=lang) + i18n.t('message.on', locale=lang)}"
            else:
                uid_hide_button.style = discord.ButtonStyle.gray
                uid_hide_button.label = f"{i18n.t('message.hide_uid', locale=lang) + i18n.t('message.off', locale=lang)}"

        def update_roll_hide_button():
            if is_roll_hide:
                roll_hide_button.style = discord.ButtonStyle.green
                roll_hide_button.label = f"{i18n.t('message.hide_roll', locale=lang) + i18n.t('message.on', locale=lang)}"
            else:
                roll_hide_button.style = discord.ButtonStyle.gray
                roll_hide_button.label = f"{i18n.t('message.hide_roll', locale=lang) + i18n.t('message.off', locale=lang)}"

        async def update_calc_selector():
            if len(json_parsed) == 0:
                calculation_selecter.options = [discord.SelectOption(label="Loading...", default=True, value="no_score")]
                return
            chara_types = []
            chara_id = json_parsed["characters"][select_number]["id"]
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{main.be_address}/weight_list/"
                                       f"{chara_id}") as response:
                    chara_type_json = await response.json()

            is_defalut_set = False
            for k, v in chara_type_json.items():
                if "lang" in v and v["lang"]["jp"] != "string" and v["lang"]["jp"] != "":
                    jp_name = v["lang"]["jp"]
                    en_name = v["lang"]["en"]
                else:
                    jp_name = i18n.t("message.compatibility_criteria", locale=lang)
                    en_name = "compatibility"

                # デフォルト値を1つだけ設定するロジック
                nonlocal calculation_value
                if not is_defalut_set and en_name == calculation_value:  # 最初の一致だけ default=True に
                    is_default = True
                    is_defalut_set = True
                else:
                    is_default = False

                chara_types.append(discord.SelectOption(label=jp_name, value=en_name, default=is_default))

            # デフォルト値が設定されなかった場合のフォールバック
            if not is_defalut_set:

                if len(chara_types) != 0:
                    calculation_value = chara_types[0].value
                    chara_types[0].default = True
                    chara_types.append(
                        discord.SelectOption(label=i18n.t("message.no_score", locale=lang), value="no_score",
                                             default=False)
                    )
                else:
                    calculation_value = "no_score"
                    chara_types.append(
                        discord.SelectOption(label=i18n.t("message.no_score", locale=lang), value="no_score",
                                             default=True)
                    )
            else:
                chara_types.append(
                    discord.SelectOption(label=i18n.t("message.no_score", locale=lang), value="no_score", default=False)
                )

            calculation_selecter.options = chara_types

        async def selector_callback(interaction):
            try:
                nonlocal select_number
                select_number = int(selecter.values[0])
                nonlocal calculation_value
                calculation_value = "compatibility"
                await update_calc_selector()
                update_selector_option()
                if len(selecter.options) != 0:
                    await ctx.edit(view=get_view())
                await interaction.response.edit_message()
            except discord.errors.HTTPException as ex:
                print(ex.text)
                pass

        async def calculation_selector_callback(interaction):
            try:
                nonlocal calculation_value
                calculation_value = calculation_selecter.values[0]
                await update_calc_selector()
                if len(selecter.options) != 0:
                    await ctx.edit(view=get_view())
                await interaction.response.edit_message()
            except discord.errors.HTTPException:
                pass

        async def uid_hide_button_callback(interaction):
            try:
                nonlocal is_uid_hide
                is_uid_hide = not is_uid_hide
                update_uid_hide_button()
                await ctx.edit(view=get_view())
                await interaction.response.edit_message()
            except discord.errors.HTTPException:
                pass

        async def roll_hide_button_callback(interaction):
            try:
                nonlocal is_roll_hide
                is_roll_hide = not is_roll_hide
                update_roll_hide_button()
                await ctx.edit(view=get_view())
                await interaction.response.edit_message()
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
                                                                 , calculating_standard=calculation_value, lang=lang,
                                                                 is_hide_roll=is_roll_hide)
                if "detail" in panel_img_result:
                    res_embed = discord.Embed(
                        title=f"Error",
                        description=panel_img_result["detail"],
                        color=discord.Colour.red(),
                    )
                    await interaction.followup.send(embed=res_embed)
                    generate_button.label = i18n.t('message.generate', locale=lang)
                    generate_button.disabled = False
                    await set_uid(uid)
                    return
                image_binary.write(panel_img_result['img'])
                # panel_img = panel_img_result['img']
                # panel_img.save(image_binary, 'PNG')
                image_binary.seek(0)
                dt_now = datetime.datetime.now()
                file = discord.File(image_binary, f"hertacardsys_{dt_now.strftime('%Y%m%d%H%M')}.png")
                res_embed = discord.Embed(
                    title=f"{json_parsed['characters'][select_number]['name']}",
                    color=discord.Colour.dark_blue(),
                )

                # 重み
                weight_text = ""
                avatar_id = json_parsed["characters"][select_number]['id']
                if calculation_value != "compatibility" and calculation_value != "no_score":
                    full_weight_dict = await get_full_weight(avatar_id + "_" + calculation_value)
                else:
                    full_weight_dict = await get_full_weight(avatar_id)

                weight_dict = full_weight_dict["weight"]
                for k, v in weight_dict.items():
                    if v == 0:
                        continue
                    weight_text += f"{i18n.t(f'message.{k}', locale=lang)}: {v}\n"
                res_embed.add_field(name=i18n.t(f'message.weight', locale=lang), value=weight_text)

                # 装備の重みとセット装備の点数
                if "relic_sets" in full_weight_dict and full_weight_dict["relic_sets"]:
                    relic_sets_text = ""
                    for relic_set in full_weight_dict["relic_sets"]:
                        set_name = await get_relic_set_name(relic_set['id'], lang)
                        relic_sets_text += f"{set_name} ({relic_set['num']}): {relic_set['weight']}\n"
                    res_embed.add_field(name=i18n.t(f'message.relic_sets', locale=lang), value=relic_sets_text)

                # 装備ごとの重み (w3: 胴, w4: 足, w5: オーブ, w6: 縄)
                if "main" in full_weight_dict:
                    main_weights = full_weight_dict["main"]
                    equipment_weights_text = ""

                    # Body (胴)
                    if "w3" in main_weights:
                        equipment_weights_text += f"**{i18n.t('message.body', locale=lang)}**:\n"
                        for k, v in main_weights["w3"].items():
                            if v == 0:
                                continue
                            equipment_weights_text += f"{i18n.t(f'message.{k}', locale=lang)}: {v}\n"
                        equipment_weights_text += "\n"

                    # Feet (足)
                    if "w4" in main_weights:
                        equipment_weights_text += f"**{i18n.t('message.feet', locale=lang)}**:\n"
                        for k, v in main_weights["w4"].items():
                            if v == 0:
                                continue
                            equipment_weights_text += f"{i18n.t(f'message.{k}', locale=lang)}: {v}\n"
                        equipment_weights_text += "\n"

                    # Orb (オーブ)
                    if "w5" in main_weights:
                        equipment_weights_text += f"**{i18n.t('message.orb', locale=lang)}**:\n"
                        for k, v in main_weights["w5"].items():
                            if v == 0:
                                continue
                            equipment_weights_text += f"{i18n.t(f'message.{k}', locale=lang)}: {v}\n"
                        equipment_weights_text += "\n"

                    # Rope (縄)
                    if "w6" in main_weights:
                        equipment_weights_text += f"**{i18n.t('message.rope', locale=lang)}**:\n"
                        for k, v in main_weights["w6"].items():
                            if v == 0:
                                continue
                            equipment_weights_text += f"{i18n.t(f'message.{k}', locale=lang)}: {v}\n"

                    if equipment_weights_text:
                        res_embed.add_field(name=i18n.t(f'message.equipment_weights', locale=lang), value=equipment_weights_text)

                score_rank = panel_img_result["header"]
                # score_rank = generate.utils.get_score_rank(int(avatar_id), uid, panel_img_result['score'])
                # 統計
                rank_text = ""
                rank_text += f"{i18n.t('message.Rank', locale=lang)}: {score_rank['rank']} / {score_rank['data_count']}\n"
                rank_text += f"{i18n.t('message.high_score', locale=lang)}: {score_rank['top_score']}\n"
                rank_text += f"{i18n.t('message.Mean', locale=lang)}: {score_rank['mean']}\n"
                rank_text += f"{i18n.t('message.Median', locale=lang)}: {score_rank['median']}\n"
                res_embed.add_field(name=i18n.t(f'message.stats', locale=lang), value=rank_text)

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

        def update_selector_option():
            count = 0
            for v in selecter.options:
                is_select = count == select_number
                selecter.options[count].default = is_select
                count += 1

        async def set_uid(changed_uid):
            nonlocal uid
            nonlocal user_detail_dict
            nonlocal json_parsed
            json_parsed = await get_json_from_url(changed_uid, lang)

            if "detail" not in json_parsed:
                embed.description = f"{i18n.t('message.nickname', locale=lang)} {json_parsed['player']['nickname']}\nUID: {json_parsed['player']['uid']}"

                user_detail_dict = json_parsed
                uid = json_parsed['player']['uid']
                selecter.options = []
                for index, i in enumerate(json_parsed["characters"]):
                    selecter.append_option(
                        discord.SelectOption(label=i["name"], value=str(index),
                                             default=True if index == select_number else False,
                                             emoji=await get_chara_emoji(i["id"])))

                if len(selecter.options) == 0:
                    embed.description += "\n" + i18n.t("message.error_no_chara_set", locale=lang)
                else:
                    await update_calc_selector()
                    await ctx.edit(view=get_view())
            elif json_parsed["detail"] == 400 or json_parsed["detail"] == 404:
                embed.description = i18n.t("message.error_not_exist_uid", locale=lang)
            elif json_parsed["detail"] == 429 or json_parsed["detail"] == 500 or json_parsed["detail"] == 503:
                embed.description = i18n.t("message.error_general_error", locale=lang)
            elif json_parsed["detail"] == 424:
                embed.description = i18n.t("message.error_game_maintenance_error", locale=lang)
            else:
                embed.description = i18n.t("message.error_queue_timeout", locale=lang)

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
        await update_calc_selector()

        calculation_selecter.row = 1
        uid_hide_button.row = 4
        uid_hide_button.callback = uid_hide_button_callback
        uid_hide_button.style = discord.ButtonStyle.gray
        uid_hide_button.label = i18n.t('message.hide_uid', locale=lang) + i18n.t('message.off', locale=lang)
        roll_hide_button.row = 4
        roll_hide_button.callback = roll_hide_button_callback
        roll_hide_button.style = discord.ButtonStyle.gray
        roll_hide_button.label = i18n.t('message.hide_roll', locale=lang) + i18n.t('message.off', locale=lang)

        embed = discord.Embed(
            title="Herta Card System",
            color=discord.Colour.dark_blue(),
            description=i18n.t("message.loading", locale=lang),
        )

        await ctx.send_followup(embed=embed, view=get_view())
        if uid is None:
            uid = await utils.DataBase.getdatabase(ctx.user.id, "uid")
        await set_uid(uid)
        return


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(CardCommand(bot))  # add the cog to the bot
