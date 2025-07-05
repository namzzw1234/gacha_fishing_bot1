# cogs/quest.py
# 🎯 ~ Nhiệm vụ Halloween hàng ngày ~ 🎃

import discord
from discord.ext import commands
import random
from utils.database import load_json, save_json
import config

class Quest(commands.Cog):
    """📜 Cog quản lý lệnh .nhiemvu – nhiệm vụ hàng ngày."""

    def __init__(self, bot):
        self.bot = bot
        self.users = load_json("users.json")
        self.quests = load_json("quests.json")

    def get_user(self, uid):
        uid = str(uid)
        if uid not in self.users:
            self.users[uid] = {
                "coins": 0,
                "level": 1,
                "exp": 0,
                "rod": "Cần Cấp 1",
                "rods_owned": ["Cần Cấp 1"],
                "equipped_bait": None,
                "equipped_hook": None,
                "fish_bag": [],
                "fish_caught": 0,
                "map": "map1",
                "character": None,
                "quests": [],
                "progress": {}
            }
        return self.users[uid]

    @commands.command()
    async def nhiemvu(self, ctx):
        """
        🎯 Lệnh .nhiemvu – xem nhiệm vụ ma quái trong đêm Halloween
        """
        if ctx.channel.id != config.ALLOWED_CHANNEL:
            return await ctx.send("⚰️ Không thể nhận nhiệm vụ ở đây!")

        user = self.get_user(ctx.author.id)

        if "quests" not in user or not user["quests"]:
            user["quests"] = random.sample(self.quests, min(3, len(self.quests)))
            user["progress"] = {}
            save_json("users.json", self.users)

        embed = discord.Embed(
            title="🗝️ 🎃 NHIỆM VỤ HALLOWEEN HẰNG NGÀY",
            description="🕯️ \"Thực hiện những lời nguyền để nhận phần thưởng...\"",
            color=0xeb984e
        )

        for q in user["quests"]:
            prog = user["progress"].get(q["id"], 0)
            done = prog >= q["amount"]
            claimed_key = f"claimed_{q['id']}"
            claimed = user.get(claimed_key, False)

            if claimed:
                status = "✅ Đã nhận thưởng"
            elif done:
                status = f"✨ Hoàn thành! Gõ `.claim {q['id']}` để nhận quà!"
            else:
                status = f"🌑 Tiến độ: {prog}/{q['amount']}"

            embed.add_field(
                name=f"🪄 {q['description']}",
                value=f"{status}\n🎁 Thưởng: {q['reward']['coins']}💰 + {q['reward']['exp']} EXP",
                inline=False
            )

        embed.set_footer(
            text="🎃 Mỗi đêm Halloween lại mang đến thử thách mới..."
        )
        await ctx.send(embed=embed)

# 📌 BẮT BUỘC CHO DISCORD.PY 2.X
async def setup(bot):
    await bot.add_cog(Quest(bot))