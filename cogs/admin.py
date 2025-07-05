# cogs/admin.py
# 🧙‍♂️ ~ Phép thuật cấm chỉ dành cho Pháp Sư Tối Cao ~ 🎃

import discord
from discord.ext import commands
from utils.database import load_json, save_json
import config

class Admin(commands.Cog):
    """📜 Cog quản lý lệnh ADMIN – chỉ chủ bot dùng được."""

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

    def is_admin(self, uid):
        return uid in config.ADMIN_IDS

    @commands.command()
    async def givecoin(self, ctx, member: discord.Member, amount: int):
        """💰 ADMIN: Cho xu người chơi"""
        if not self.is_admin(ctx.author.id):
            return await ctx.send("⚰️ Phép cấm! Ngươi không đủ quyền năng!")

        user = self.get_user(member.id)
        user["coins"] += amount
        save_json("users.json", self.users)

        await ctx.send(f"💰 Đã ban thưởng {amount}💰 cho **{member.display_name}**. Hãy tiêu xài khôn ngoan trong chợ ma!")

    @commands.command()
    async def setlevel(self, ctx, member: discord.Member, level: int):
        """🪄 ADMIN: Set level người chơi"""
        if not self.is_admin(ctx.author.id):
            return await ctx.send("⚰️ Phép cấm! Ngươi không đủ quyền năng!")

        user = self.get_user(member.id)
        user["level"] = level
        save_json("users.json", self.users)

        await ctx.send(f"🧙‍♂️ Đã phù phép set level {level} cho **{member.display_name}**.")

    @commands.command()
    async def resetuser(self, ctx, member: discord.Member):
        """⚰️ ADMIN: Reset data người chơi"""
        if not self.is_admin(ctx.author.id):
            return await ctx.send("⚰️ Phép cấm! Ngươi không đủ quyền năng!")

        uid = str(member.id)
        if uid in self.users:
            del self.users[uid]
            save_json("users.json", self.users)
            await ctx.send(f"💀 Dữ liệu của **{member.display_name}** đã bị xóa sạch khỏi sổ phép thuật!")
        else:
            await ctx.send("👻 Không tìm thấy user này trong sổ phép thuật.")

    @commands.command()
    async def adminsay(self, ctx, *, message):
        """👻 ADMIN: Bot nói câu bất kỳ"""
        if not self.is_admin(ctx.author.id):
            return await ctx.send("⚰️ Phép cấm! Ngươi không đủ quyền năng!")

        await ctx.send(f"🕯️ {message}")

# 📌 BẮT BUỘC CHO DISCORD.PY 2.X
async def setup(bot):
    await bot.add_cog(Admin(bot))