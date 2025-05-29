import io
import json
import os

import discord
import i18n
from discord.ext import commands
from discord.ui import Select, Button, Modal, View

import main
import utils.Weight
from generate.utils import get_mihomo_lang


async def get_relic_sets():
    """Load relic sets from the JSON file."""
    # Use absolute path to ensure file is found regardless of current working directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    relic_sets_path = os.path.join(base_dir, "generate", "StarRailRes", "index_min", "jp", "relic_sets.json")
    with open(relic_sets_path, "r", encoding="utf-8") as f:
        relic_sets = json.load(f)
    return relic_sets


class CreateWeightCommand(commands.Cog):

    async def get_chara_types(ctx: discord.AutocompleteContext):
        return main.characters

    @discord.slash_command(name="create_weight", description="Create weight", guild_ids=["1118740618882072596"])
    async def create_weight_command(self, ctx,
                                    chara_id: discord.Option(required=True, description="キャラ", input_type=str,
                                                             autocomplete=discord.utils.basic_autocomplete(
                                                                 main.characters)),
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
            for k, v in weight.main.w5.model_dump().items():
                embed_value += f"{i18n.t('message.' + k, locale=lang)}: {v}\n"
            embed.add_field(name="オーブ", value=embed_value)
            embed_value = ""
            for k, v in weight.main.w6.model_dump().items():
                embed_value += f"{i18n.t('message.' + k, locale=lang)}: {v}\n"
            embed.add_field(name="縄", value=embed_value)
            embed_value = ""
            for k, v in weight.weight.model_dump().items():
                embed_value += f"{i18n.t('message.' + k, locale=lang)}: {v}\n"
            embed.add_field(name="サブステ", value=embed_value)

            # Display relic_sets
            if weight.relic_sets:
                embed_value = ""
                relic_sets_data = await get_relic_sets()
                for relic_set in weight.relic_sets:
                    relic_name = relic_sets_data.get(relic_set.id, {}).get("name", relic_set.id)
                    embed_value += f"{relic_name}: {relic_set.weight} ({relic_set.num}セット)\n"
                embed.add_field(name="遺物セット", value=embed_value)

            await ctx.interaction.edit(embed=embed)

        class MyView(discord.ui.View):
            def __init__(self, *args, **kwargs):
                super().__init__(timeout=3600, *args, **kwargs)
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

            @discord.ui.button(label="遺物セット")
            async def button_callback_relic_sets(self, button, interaction):
                # Create and show the RelicSetView instead of the modal
                relic_set_view = RelicSetView(title="遺物セット")
                await relic_set_view.initialize()
                await interaction.response.send_message("遺物セットを選択してください", view=relic_set_view, ephemeral=True)

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

        class RelicSetView(discord.ui.View):
            def __init__(self, title, *args, **kwargs) -> None:
                super().__init__(timeout=3600, *args, **kwargs)
                self.title = title
                self.relic_sets_data = {}
                self.selected_set_id = None
                self.selected_set_name = None
                self.current_page = 0
                self.items_per_page = 24  # Maximum 25 options in a Select, leave room for instructions
                self.total_pages = 0
                self.all_set_ids = []

                # Create selector for relic sets
                self.relic_set_selector = Select(placeholder="遺物セットを選択してください")
                self.relic_set_selector.callback = self.relic_set_selected
                self.add_item(self.relic_set_selector)

                # Create input for weight
                self.weight_input = discord.ui.InputText(
                    label="重み（最大30点）",
                    placeholder="例: 10",
                    min_length=1,
                    max_length=5,
                    required=True
                )

                # Create selector for num (2 or 4)
                self.num_selector = Select(placeholder="セット数を選択してください")
                self.num_selector.add_option(label="2セット", value="2", default=True)
                self.num_selector.add_option(label="4セット", value="4")
                self.num_selector.callback = self.num_selected
                self.add_item(self.num_selector)

                # Create pagination buttons
                self.prev_button = Button(label="前のページ", style=discord.ButtonStyle.secondary)
                self.prev_button.callback = self.prev_page
                self.add_item(self.prev_button)

                self.next_button = Button(label="次のページ", style=discord.ButtonStyle.secondary)
                self.next_button.callback = self.next_page
                self.add_item(self.next_button)

                # Create button to add the relic set
                self.add_button = Button(label="追加", style=discord.ButtonStyle.primary)
                self.add_button.callback = self.add_relic_set
                self.add_item(self.add_button)

                # Create button to finish
                self.finish_button = Button(label="完了", style=discord.ButtonStyle.success)
                self.finish_button.callback = self.finish
                self.add_item(self.finish_button)

            async def initialize(self):
                # Load relic sets data
                self.relic_sets_data = await get_relic_sets()

                # Store all set IDs for pagination
                self.all_set_ids = list(self.relic_sets_data.keys())
                self.total_pages = (len(self.all_set_ids) + self.items_per_page - 1) // self.items_per_page

                # Update pagination buttons
                self.update_pagination_buttons()

                # Load the first page of options
                await self.load_page(0)

            async def load_page(self, page):
                # Clear existing options
                self.relic_set_selector.options = []

                # Calculate start and end indices for the current page
                start_idx = page * self.items_per_page
                end_idx = min(start_idx + self.items_per_page, len(self.all_set_ids))

                # Add page indicator option
                self.relic_set_selector.add_option(
                    label=f"ページ {page + 1}/{self.total_pages}",
                    value="page_indicator",
                    default=True
                )

                # Add options for the current page
                for i in range(start_idx, end_idx):
                    set_id = self.all_set_ids[i]
                    set_data = self.relic_sets_data.get(set_id, {})
                    self.relic_set_selector.add_option(
                        label=set_data.get("name", set_id),
                        value=set_id,
                        default=False
                    )

                # Update current page
                self.current_page = page

                # Update pagination buttons
                self.update_pagination_buttons()

            def update_pagination_buttons(self):
                # Disable prev button if on first page
                self.prev_button.disabled = (self.current_page == 0)

                # Disable next button if on last page
                self.next_button.disabled = (self.current_page >= self.total_pages - 1)

            async def prev_page(self, interaction):
                if self.current_page > 0:
                    await self.load_page(self.current_page - 1)
                    await interaction.response.edit_message(view=self)
                else:
                    await interaction.response.defer()

            async def next_page(self, interaction):
                if self.current_page < self.total_pages - 1:
                    await self.load_page(self.current_page + 1)
                    await interaction.response.edit_message(view=self)
                else:
                    await interaction.response.defer()

            async def num_selected(self, interaction):
                # Respond to the interaction to prevent the "Interaction failed" error
                await interaction.response.defer()

            async def relic_set_selected(self, interaction):
                selected_value = self.relic_set_selector.values[0]

                # Skip if page indicator is selected
                if selected_value == "page_indicator":
                    await interaction.response.defer()
                    return

                self.selected_set_id = selected_value
                self.selected_set_name = self.relic_sets_data.get(self.selected_set_id, {}).get("name", self.selected_set_id)

                # Get current weight and num if exists
                current_weight = 0
                current_num = 2

                # Get the currently selected num value
                selected_num = int(self.num_selector.values[0]) if self.num_selector.values else 2

                # First try to find a relic set with matching ID and num
                for relic_set in weight.relic_sets:
                    if relic_set.id == self.selected_set_id and relic_set.num == selected_num:
                        current_weight = relic_set.weight
                        current_num = relic_set.num
                        break
                # If not found, try to find any relic set with matching ID
                else:
                    for relic_set in weight.relic_sets:
                        if relic_set.id == self.selected_set_id:
                            current_weight = relic_set.weight
                            current_num = relic_set.num
                            break

                # Update num selector
                for option in self.num_selector.options:
                    option.default = (option.value == str(current_num))

                # Show a modal to input the weight
                modal = discord.ui.Modal(title=f"{self.selected_set_name}の重みを設定")
                self.weight_input.value = str(current_weight) if current_weight else ""
                modal.add_item(self.weight_input)

                async def modal_callback(modal_interaction):
                    await modal_interaction.response.defer()

                modal.callback = modal_callback
                await interaction.response.send_modal(modal)

            async def add_relic_set(self, interaction):
                if not self.selected_set_id or not self.weight_input.value:
                    await interaction.response.send_message("遺物セットと重みを選択してください", ephemeral=True)
                    return

                try:
                    weight_value = float(self.weight_input.value)
                    if  weight_value > 30 or weight_value < 0:
                        await interaction.response.send_message("30以下の数字を入れてください。", ephemeral=True)
                        return
                    num_value = int(self.num_selector.values[0]) if self.num_selector.values else 2

                    # Add or update the relic set
                    for i, relic_set in enumerate(weight.relic_sets):
                        if relic_set.id == self.selected_set_id and relic_set.num == num_value:
                            weight.relic_sets[i].weight = weight_value
                            break
                    else:
                        weight.relic_sets.append(utils.Weight.RelicSetWeight(
                            id=self.selected_set_id,
                            weight=weight_value,
                            num=num_value
                        ))

                    # Update the embed
                    await update_embed()
                    await interaction.response.send_message(
                        f"{self.selected_set_name}を追加しました（重み: {weight_value}, セット数: {num_value}）",
                        ephemeral=True
                    )

                    # Reset the selected set
                    self.selected_set_id = None
                    self.selected_set_name = None
                    self.weight_input.value = ""

                except ValueError:
                    await interaction.response.send_message("重みは数値で入力してください", ephemeral=True)

            async def finish(self, interaction):
                await interaction.response.edit_message(content="遺物セットの設定を完了しました", view=None)

        # Keep the old modal for backward compatibility
        class ModalRelicSets(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                # Get existing relic set weights and nums
                relic_set_data = []
                for relic_set in weight.relic_sets:
                    relic_set_data.append({
                        "id": relic_set.id,
                        "weight": relic_set.weight,
                        "num": relic_set.num
                    })

                # Add instructions
                self.add_item(
                    discord.ui.InputText(label="遺物セットの重みを設定（最大30点）",
                                         style=discord.InputTextStyle.paragraph,
                                         value="形式: セットID:重み:セット数（例: 101:10:2,102:5:4）\nセット数は2または4",
                                         required=False))

                # Add current values
                current_values = ""
                if relic_set_data:
                    current_values = ",".join([f"{data['id']}:{data['weight']}:{data['num']}" for data in relic_set_data])

                self.add_item(
                    discord.ui.InputText(label="現在の設定値",
                                         style=discord.InputTextStyle.paragraph,
                                         value=current_values,
                                         required=True))

            async def callback(self, interaction: discord.Interaction):
                # Parse the input
                relic_sets_input = self.children[1].value

                # Clear existing relic sets
                weight.relic_sets = []

                # Parse and add new relic sets
                if relic_sets_input:
                    pairs = relic_sets_input.split(",")
                    for pair in pairs:
                        parts = pair.split(":")
                        if len(parts) >= 2:  # At least id and weight
                            id_str = parts[0].strip()
                            weight_str = parts[1].strip()

                            # Default num to 2 if not provided
                            num_value = 2

                            # If num is provided, use it
                            if len(parts) >= 3:
                                try:
                                    num_str = parts[2].strip()
                                    num_value = int(num_str)
                                    # Ensure num is either 2 or 4
                                    if num_value != 2 and num_value != 4:
                                        num_value = 2
                                except ValueError:
                                    pass

                            try:
                                weight_value = float(weight_str)
                                weight.relic_sets.append(utils.Weight.RelicSetWeight(
                                    id=id_str,
                                    weight=weight_value,
                                    num=num_value
                                ))
                            except ValueError:
                                pass

                await update_embed()
                await interaction.response.defer()

        await ctx.send_followup(view=MyView())
        await update_embed()


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(CreateWeightCommand(bot))  # add the cog to the bot
