# cogs/fishing.py
# 🎣 ~ Nghề câu cá ma quái trong đêm Halloween ~ 🕯️

import discord
from discord.ext import commands
from discord.ui import View, Select
import asyncio
import random
import os
from utils.database import load_json, save_json
import config

class Fishing(commands.Cog):
    """📜 Cog quản lý nghề câu cá phép thuật."""

    def __init__(self, bot):
        self.bot = bot
        self.users = load_json("users.json")
        self.fishes = load_json("fishes.json")
        self.maps = load_json("maps.json")
        self.rods = load_json("rods.json")

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

    # 🎣 LỆNH .cau – Thả cần
    @commands.command()
    async def cau(self, ctx):
        if ctx.channel.id != config.ALLOWED_CHANNEL:
            return await ctx.send("⚰️ Không được thả cần ở đây!")

        user = self.get_user(ctx.author.id)
        current_map = next((m for m in self.maps if m["id"] == user.get("map")), self.maps[0])
        rates = current_map.get("rarity_rates", {"common": 90, "rare": 10, "legendary": 0})
        rates["halloween"] = 5

        fishing_msg = await ctx.send(
            "🌙 Dưới ánh trăng máu, bạn lặng lẽ thả cần tìm sinh vật bí ẩn... 🐟",
            file=discord.File("images/animations/luffy_fishing.gif")
        )

        await asyncio.sleep(5)

        total = sum(rates.values())
        rand = random.randint(1, total)
        acc = 0
        rarity = "common"
        for k, v in rates.items():
            acc += v
            if rand <= acc:
                rarity = k
                break

        possible = [f for f in self.fishes.get(rarity, []) if str(f.get("map", "")) == str(current_map["id"])]
        if not possible:
            possible = self.fishes.get(rarity, [])
        if not possible:
            await fishing_msg.delete()
            return await ctx.send("🐟 Gió lạnh thổi qua – không có cá nào xuất hiện!", delete_after=10)

        fish = random.choice(possible)
        size = round(random.uniform(fish.get("min_cm", 10), fish.get("max_cm", 50)), 1)

        fish_copy = dict(fish)
        fish_copy["length_cm"] = size
        user["fish_bag"].append(fish_copy)
        user["fish_caught"] += 1
        user["exp"] += fish_copy.get("exp", 5)
        save_json("users.json", self.users)

        emoji_map = {"legendary": "💎", "rare": "🔮", "common": "🐟", "halloween": "🎃"}
        emoji = emoji_map.get(rarity, "🐟")

        embed = discord.Embed(
            title=f"{emoji} {ctx.author.display_name} đã câu được {emoji} **{fish_copy['name']}**!",
            description=(
                f"📏 Kích cỡ: {size}cm\n"
                f"💰 Giá bán: {fish_copy.get('base_price', 10)} xu\n"
                f"🌊 Vùng biển: {current_map['name']}\n"
                f"🕯️ Dưới ánh trăng Halloween..."
            ),
            color=0xeb984e
        )
        embed.set_footer(text="🎃 Đêm Halloween luôn giấu những sinh vật đáng sợ...")

        try:
            file = discord.File(fish_copy["image"], filename="fish.png")
            embed.set_image(url="attachment://fish.png")
            await fishing_msg.delete()
            await ctx.send(embed=embed, file=file)
        except Exception as e:
            await fishing_msg.delete()
            await ctx.send(embed=embed)
            print(f"[ERROR] Không thể gửi ảnh cá: {e}")

    # 🎒 LỆNH .balo
    @commands.command()
    async def balo(self, ctx, page: int = 1):
        if ctx.channel.id != config.ALLOWED_CHANNEL:
            return await ctx.send("⚰️ Đây không phải nơi kiểm tra balo phép thuật!")

        user = self.get_user(ctx.author.id)
        fish_bag = user.get("fish_bag", [])

        if not fish_bag:
            return await ctx.send("🍬 Balo trống rỗng – hãy đi câu thêm!", delete_after=10)

        per_page = 10
        max_page = (len(fish_bag) - 1) // per_page + 1
        page = max(1, min(page, max_page))
        start = (page - 1) * per_page
        end = start + per_page

        desc = ""
        for i, fish in enumerate(fish_bag[start:end], start=start + 1):
            emoji = "🐟"
            name = f"**{fish['name']}**"
            desc += f"`{i}` {emoji} {name} | 📏 {fish['length_cm']}cm | 💰 {fish['base_price']} xu\n"

        embed = discord.Embed(
            title=f"🎒 Balo Phép Thuật: {ctx.author.display_name} [Trang {page}/{max_page}]",
            description=desc,
            color=0x9b59b6,
        )
        embed.set_footer(text="🎃 Trong đêm Halloween, balo đầy lời nguyền...")
        await ctx.send(embed=embed)

    # 🧙‍♂️ LỆNH .trangbi
    @commands.command()
    async def trangbi(self, ctx):
        if ctx.channel.id != config.ALLOWED_CHANNEL:
            return await ctx.send("⚰️ Không thể xem trang bị ở đây!")

        user = self.get_user(ctx.author.id)

        embed = discord.Embed(
            title=f"🧙‍♂️ Trang Bị Phép Thuật của {ctx.author.display_name}",
            description="🕯️ Một danh sách vật phẩm bị phong ấn...",
            color=0x9b59b6
        )

        embed.add_field(name="🎣 Cần phép", value=user.get("rod", "Không"), inline=False)
        embed.add_field(name="🪱 Mồi", value=user.get("equipped_bait") or "Không", inline=False)
        embed.add_field(name="🪝 Lưỡi", value=user.get("equipped_hook") or "Không", inline=False)
        embed.add_field(name="💰 Xu hiện có", value=f"{user.get('coins', 0)}", inline=False)
        embed.add_field(name="✨ Level", value=f"{user.get('level', 1)}", inline=False)
        embed.set_footer(text="🎃 Trong đêm Halloween, vũ khí tốt quyết định sống còn...")

        await ctx.send(embed=embed)

# 📌 BẮT BUỘC CHO DISCORD.PY 2.X
async def setup(bot):
    await bot.add_cog(Fishing(bot))