import datetime
import io

import discord
import i18n
from discord.ext import commands
from discord.ui import Select, Button, Modal, View

import main
import utils.Weight
from generate.generate import generate_panel
from generate.utils import get_json_from_url, get_mihomo_lang


class CreateWeightCommand(commands.Cog):

    async def get_chara_types(ctx: discord.AutocompleteContext):
        return main.characters

    @discord.slash_command(name="create_weight", description="Create weight", guild_ids=["1118740618882072596"])
    async def create_weight_command(self, ctx,
                                    chara_id: discord.Option(required=True, description="キャラ", input_type=str,
                                                             options=main.characters),
                                    jp_name: discord.Option(required=True, description="基準の日本語名（攻撃型、回復型など）"),
                                    en_name: discord.Option(required=True, description="基準の英語名・スペース、記号禁止（attack、healなど）")):
        await ctx.defer()
        weight = utils.Weight.Weight()
        lang = get_mihomo_lang(ctx.interaction.locale)
        embed = discord.Embed(
            title=main.characters_name[chara_id]
        )
        weight.lang.jp = jp_name
        weight.lang.en = en_name

        async def update_embed():
            embed = discord.Embed(
                title=f"{main.characters_name[chara_id]}・{jp_name}(投票中)",
                description="追加申請",
                colour=discord.Colour.gold()
            )
            embed_value = ""
            for k, v in weight.main.w3.model_dump().items():
                embed_value += f"{i18n.t('message.' + k, locale=lang)}: {v}\n"
            embed.add_field(name="胴", value=embed_value)
            embed_value = ""
            for k, v in weight.main.w4.model_dump().items():
                embed_value += f"{i18n.t('message.' + k, locale=lang)}: {v}\n"
            embed.add_field(name="脚", value=embed_value)
            embed_value = ""
            for k, v in weight.main.w4.model_dump().items():
                embed_value += f"{i18n.t('message.' + k, locale=lang)}: {v}\n"
            embed.add_field(name="オーブ", value=embed_value)
            embed_value = ""
            for k, v in weight.main.w5.model_dump().items():
                embed_value += f"{i18n.t('message.' + k, locale=lang)}: {v}\n"
            embed.add_field(name="縄", value=embed_value)
            embed_value = ""
            for k, v in weight.weight.model_dump().items():
                embed_value += f"{i18n.t('message.' + k, locale=lang)}: {v}\n"
            embed.add_field(name="サブステ", value=embed_value)
            await ctx.interaction.edit(embed=embed)

        class MyView(discord.ui.View):
            @discord.ui.button(label="胴1")
            async def button_callback_31(self, button, interaction):
                await interaction.response.send_modal(Modal31(title="胴1"))

            @discord.ui.button(label="胴2")
            async def button_callback_32(self, button, interaction):
                await interaction.response.send_modal(Modal32(title="胴2"))

            @discord.ui.button(label="脚1")
            async def button_callback_41(self, button, interaction):
                await interaction.response.send_modal(Modal41(title="脚1"))

            @discord.ui.button(label="オーブ1")
            async def button_callback_51(self, button, interaction):
                await interaction.response.send_modal(Modal51(title="オーブ1"))

            @discord.ui.button(label="オーブ2")
            async def button_callback_52(self, button, interaction):
                await interaction.response.send_modal(Modal52(title="オーブ2"))

            @discord.ui.button(label="縄1")
            async def button_callback_61(self, button, interaction):
                await interaction.response.send_modal(Modal61(title="縄1"))

            @discord.ui.button(label="サブステ1")
            async def button_callback_s1(self, button, interaction):
                await interaction.response.send_modal(Modals1(title="サブステ1"))

            @discord.ui.button(label="サブステ2")
            async def button_callback_s2(self, button, interaction):
                await interaction.response.send_modal(Modals2(title="サブステ2"))

            @discord.ui.button(label="サブステ3")
            async def button_callback_s3(self, button, interaction):
                await interaction.response.send_modal(Modals3(title="サブステ3"))

            @discord.ui.button(label="送信", style=discord.ButtonStyle.primary)
            async def button_callback_send(self, button, interaction):
                attachment = discord.File(fp=io.BytesIO(bytes(weight.model_dump_json(), encoding="utf-8")), filename=f"{chara_id}.json")
                await interaction.edit(file=attachment, view=None)
                await interaction.message.add_reaction("⭕")
                await interaction.message.add_reaction("❌")
                await interaction.message.create_thread(name="申請理由など")

        class Modal31(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.HPAddedRatio', locale=lang), min_length=3, max_length=3,
                                         value=str(weight.main.w3.HPAddedRatio)))
                self.add_item(discord.ui.InputText(label=i18n.t('message.AttackAddedRatio', locale=lang), min_length=3,
                                                   max_length=3, value=str(weight.main.w3.AttackAddedRatio)))
                self.add_item(discord.ui.InputText(label=i18n.t('message.DefenceAddedRatio', locale=lang), min_length=3,
                                                   max_length=3, value=str(weight.main.w3.DefenceAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.CriticalChanceBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w3.CriticalChanceBase)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.CriticalDamageBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w3.CriticalDamageBase)))

            async def callback(self, interaction: discord.Interaction):
                weight.main.w3.HPAddedRatio = float(self.children[0].value)
                weight.main.w3.AttackAddedRatio = float(self.children[1].value)
                weight.main.w3.DefenceAddedRatio = float(self.children[2].value)
                weight.main.w3.CriticalChanceBase = float(self.children[3].value)
                weight.main.w3.CriticalDamageBase = float(self.children[4].value)
                await update_embed()
                await interaction.response.defer()

        class Modal32(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.HealRatioBase', locale=lang), min_length=3, max_length=3,
                                         value=str(weight.main.w3.HealRatioBase)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.StatusProbabilityBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w3.StatusProbabilityBase)))

            async def callback(self, interaction: discord.Interaction):
                weight.main.w3.HealRatioBase = float(self.children[0].value)
                weight.main.w3.StatusProbabilityBase = float(self.children[1].value)
                await update_embed()
                await interaction.response.defer()

        class Modal41(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.HPAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w4.HPAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.AttackAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w4.AttackAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.DefenceAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w4.DefenceAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.SpeedDelta', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w4.SpeedDelta)))

            async def callback(self, interaction: discord.Interaction):
                weight.main.w4.HPAddedRatio = float(self.children[0].value)
                weight.main.w4.AttackAddedRatio = float(self.children[1].value)
                weight.main.w4.DefenceAddedRatio = float(self.children[2].value)
                weight.main.w4.SpeedDelta = float(self.children[3].value)
                await update_embed()
                await interaction.response.defer()

        class Modal51(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.HPAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.HPAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.AttackAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.AttackAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.DefenceAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.DefenceAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.PhysicalAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.PhysicalAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.FireAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.FireAddedRatio)))

            async def callback(self, interaction: discord.Interaction):
                weight.main.w5.HPAddedRatio = float(self.children[0].value)
                weight.main.w5.AttackAddedRatio = float(self.children[1].value)
                weight.main.w5.DefenceAddedRatio = float(self.children[2].value)
                weight.main.w5.PhysicalAddedRatio = float(self.children[3].value)
                weight.main.w5.FireAddedRatio = float(self.children[4].value)
                await update_embed()
                await interaction.response.defer()

        class Modal52(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.IceAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.IceAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.ThunderAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.ThunderAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.WindAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.WindAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.QuantumAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.QuantumAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.ImaginaryAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w5.ImaginaryAddedRatio)))

            async def callback(self, interaction: discord.Interaction):
                weight.main.w5.IceAddedRatio = float(self.children[0].value)
                weight.main.w5.ThunderAddedRatio = float(self.children[1].value)
                weight.main.w5.WindAddedRatio = float(self.children[2].value)
                weight.main.w5.QuantumAddedRatio = float(self.children[3].value)
                weight.main.w5.ImaginaryAddedRatio = float(self.children[4].value)
                await update_embed()
                await interaction.response.defer()

        class Modal61(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.BreakDamageAddedRatioBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w6.BreakDamageAddedRatioBase)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.SPRatioBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w6.SPRatioBase)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.HPAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w6.HPAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.AttackAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w6.AttackAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.DefenceAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.main.w6.DefenceAddedRatio)))

            async def callback(self, interaction: discord.Interaction):
                weight.main.w6.BreakDamageAddedRatioBase = float(self.children[0].value)
                weight.main.w6.SPRatioBase = float(self.children[1].value)
                weight.main.w6.HPAddedRatio = float(self.children[2].value)
                weight.main.w6.AttackAddedRatio = float(self.children[3].value)
                weight.main.w6.DefenceAddedRatio = float(self.children[4].value)
                await update_embed()
                await interaction.response.defer()

        class Modals1(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.HPDelta', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.HPDelta)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.AttackDelta', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.AttackDelta)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.DefenceDelta', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.DefenceDelta)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.HPAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.HPAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.AttackAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.AttackAddedRatio)))

            async def callback(self, interaction: discord.Interaction):
                weight.weight.HPDelta = float(self.children[0].value)
                weight.weight.AttackDelta = float(self.children[1].value)
                weight.weight.DefenceDelta = float(self.children[2].value)
                weight.weight.HPAddedRatio = float(self.children[3].value)
                weight.weight.AttackAddedRatio = float(self.children[4].value)
                await update_embed()
                await interaction.response.defer()

        class Modals2(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.DefenceAddedRatio', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.DefenceAddedRatio)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.SpeedDelta', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.SpeedDelta)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.CriticalChanceBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.CriticalChanceBase)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.CriticalDamageBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.CriticalDamageBase)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.StatusProbabilityBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.StatusProbabilityBase)))

            async def callback(self, interaction: discord.Interaction):
                weight.weight.DefenceAddedRatio = float(self.children[0].value)
                weight.weight.SpeedDelta = float(self.children[1].value)
                weight.weight.CriticalChanceBase = float(self.children[2].value)
                weight.weight.CriticalDamageBase = float(self.children[3].value)
                weight.weight.StatusProbabilityBase = float(self.children[4].value)
                await update_embed()
                await interaction.response.defer()

        class Modals3(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.StatusResistanceBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.StatusResistanceBase)))
                self.add_item(
                    discord.ui.InputText(label=i18n.t('message.BreakDamageAddedRatioBase', locale=lang), min_length=3,
                                         max_length=3, value=str(weight.weight.BreakDamageAddedRatioBase)))

            async def callback(self, interaction: discord.Interaction):
                weight.weight.StatusResistanceBase = float(self.children[0].value)
                weight.weight.BreakDamageAddedRatioBase = float(self.children[1].value)
                await update_embed()
                await interaction.response.defer()

        await ctx.send_followup(view=MyView())
        await update_embed()


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(CreateWeightCommand(bot))  # add the cog to the bot
