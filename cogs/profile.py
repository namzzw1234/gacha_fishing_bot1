# cogs/profile.py
# 🧙‍♂️ ~ Hồ sơ phép thuật Halloween của người chơi ~ 🎃

import discord
from discord.ext import commands
from utils.database import load_json, save_json
import config

class Profile(commands.Cog):
    """📜 Cog quản lý lệnh hồ sơ người chơi."""

    def __init__(self, bot):
        self.bot = bot
        self.users = load_json("users.json")

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
                "character": None
            }
        return self.users[uid]

    @commands.command()
    async def hoso(self, ctx):
        """
        📜 Lệnh .hoso – hiện hồ sơ phép thuật
        Embed ma mị Halloween 🎃
        """
        if ctx.channel.id != config.ALLOWED_CHANNEL:
            return await ctx.send("⚰️ Kênh này không được phép triệu hồi phép thuật!")

        user = self.get_user(ctx.author.id)

        embed = discord.Embed(
            title=f"🕯️ Hồ sơ phép thuật của {ctx.author.display_name}",
            description="📜 Một cuộn giấy cổ xưa rít gió dưới ánh trăng máu...",
            color=0x9b59b6
        )
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.add_field(name="🎃 Level", value=user.get("level", 1))
        embed.add_field(name="🦇 EXP", value=user.get("exp", 0))
        embed.add_field(name="💰 Xu", value=f"{user.get('coins', 0)}")
        embed.add_field(name="🎣 Cần phép", value=user.get("rod", "Không"))
        embed.add_field(name="🪱 Mồi", value=user.get("equipped_bait") or "Không")
        embed.add_field(name="🪝 Lưỡi", value=user.get("equipped_hook") or "Không")
        embed.add_field(name="🐟 Tổng cá câu", value=user.get("fish_caught", 0))
        embed.set_footer(
            text="🎃 Hồ sơ bị phong ấn trong đêm Halloween – chỉ kẻ dũng cảm mới dám mở!"
        )
        await ctx.send(embed=embed)

# 📌 BẮT BUỘC CHO DISCORD.PY 2.X
async def setup(bot):
    await bot.add_cog(Profile(bot))