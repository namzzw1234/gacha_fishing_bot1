# cogs/leaderboard.py
# 🏆 ~ Bảng Vinh Danh Halloween ~ 🎃

import discord
from discord.ext import commands
import config
from utils.database import load_json

class Leaderboard(commands.Cog):
    """📜 Cog quản lý lệnh .top – bảng xếp hạng thợ câu ma quái."""

    def __init__(self, bot):
        self.bot = bot
        self.users = load_json("users.json")

    @commands.command()
    async def top(self, ctx):
        """
        🏆 Lệnh .top – bảng xếp hạng top 10 theo EXP
        """
        if ctx.channel.id != config.ALLOWED_CHANNEL:
            return await ctx.send("⚰️ Không thể xem bảng vinh danh ở đây!")

        # Sort users theo EXP giảm dần
        top_users = sorted(
            self.users.items(),
            key=lambda x: x[1].get("exp", 0),
            reverse=True
        )[:10]

        icons = ["🥇", "🥈", "🥉"] + ["🎃"] * 7
        embed = discord.Embed(
            title="🏆 🎃 BẢNG VINH DANH HALLOWEEN",
            description="🕯️ \"Chỉ những kẻ liều lĩnh nhất mới có tên trong cuộn giấy cổ xưa...\"",
            color=0xeb984e
        )

        if not top_users:
            embed.add_field(
                name="👻 Trống rỗng...",
                value="⚰️ Chưa có ai dám bước vào đêm săn cá ma quái.",
                inline=False
            )
        else:
            for i, (uid, data) in enumerate(top_users, 1):
                try:
                    member = await self.bot.fetch_user(int(uid))
                    name = member.display_name
                except:
                    name = f"Hồn ma {uid}"

                level = data.get("level", 1)
                exp = data.get("exp", 0)

                embed.add_field(
                    name=f"{icons[i - 1]} #{i} – {name}",
                    value=f"✨ Level: {level} | 👻 EXP: {exp}",
                    inline=False
                )

        embed.set_footer(
            text="🎃 Ai sẽ trở thành huyền thoại Halloween tiếp theo?"
        )
        await ctx.send(embed=embed)

# 📌 BẮT BUỘC CHO DISCORD.PY 2.X
async def setup(bot):
    await bot.add_cog(Leaderboard(bot))