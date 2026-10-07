import io
import json

import aiohttp
import discord
from discord.ext import commands

import main
from commands.ChangeWeightCommand import ChangeWeightCommand


class ResetScoreCommand(commands.Cog):

    @discord.slash_command(name="reset_score", description="Reset score", guild_ids=["1118740618882072596"])
    async def reset_score_command(self, ctx,
                                  chara_id: discord.Option(required=True, description="キャラ", input_type=str,
                                                           autocomplete=discord.utils.basic_autocomplete(
                                                               main.characters)),
                                  type_id: discord.Option(required=True, description="基準名", input_type=str,
                                                          autocomplete=discord.utils.basic_autocomplete(
                                                              ChangeWeightCommand.get_chara_types)),
                                  min_score: discord.Option(int, required=True, description="このスコア以上の登録を削除",
                                                            min_value=0)):
        await ctx.defer()
        resolved_chara = main.resolve_chara_id(chara_id)
        if resolved_chara is None:
            await ctx.send_followup("存在しないキャラクターです")
            return
        chara_id = resolved_chara

        # type_id を日本語名/英語名から解決
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{main.be_address}/weight_list/{chara_id}") as response:
                type_list_json = await response.json()
        valid_types = {}
        for v in type_list_json.values():
            if "lang" in v and v["lang"]["jp"] != "string" and v["lang"]["jp"] != "":
                valid_types[v["lang"]["en"]] = v["lang"]
                valid_types[v["lang"]["jp"]] = v["lang"]
            else:
                valid_types["def"] = valid_types["相性基準"] = {"jp": "相性基準", "en": "compatibility"}
        if type_id not in valid_types:
            await ctx.send_followup("存在しない基準名です")
            return
        type_lang = valid_types[type_id]

        embed = discord.Embed(
            title=f"{main.characters_name[chara_id]}・{type_lang['jp']}(投票中)",
            description="スコアリセット申請",
            colour=discord.Colour.gold()
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{main.be_address}/scores/{chara_id}/distribution",
                                   params={"calculation_value": type_lang["en"], "bins": 15,
                                           "min_score": min_score}) as response:
                dist = await response.json()
        embed.add_field(name="削除対象", value=f"スコア{min_score}以上（{dist['above']}/{dist['count']}件）")
        if dist["count"] > 0:
            max_count = max(b["count"] for b in dist["bins"])
            lines = [f"{b['start']:>4} {('▒' if b['start'] >= min_score else '█') * round(b['count'] / max_count * 15)} {b['count']}"
                     for b in dist["bins"]]
            embed.add_field(name=f"スコア分布（{dist['bin_width']}刻み・▒は削除対象）",
                            value="```\n" + "\n".join(lines) + "\n```", inline=False)
        reset_json = {"calculation_value": type_lang["en"], "min_score": min_score}
        attachment = discord.File(fp=io.BytesIO(bytes(json.dumps(reset_json), encoding="utf-8")),
                                  filename=f"{chara_id}.json")
        message = await ctx.send_followup(embed=embed, file=attachment)
        await message.add_reaction("⭕")
        await message.add_reaction("❌")
        await message.create_thread(name="申請理由など")


def setup(bot):
    bot.add_cog(ResetScoreCommand(bot))
