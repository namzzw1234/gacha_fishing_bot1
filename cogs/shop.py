# cogs/shop.py
# 🎃 ~ Chợ phép thuật Halloween ~ 🕯️

import discord
from discord.ext import commands
from discord.ui import View, Select
from utils.database import load_json, save_json
import config

class Shop(commands.Cog):
    """📜 Cog quản lý lệnh .shop – mua bán vật phẩm ma quái."""

    def __init__(self, bot):
        self.bot = bot
        self.users = load_json("users.json")
        self.items = load_json("items.json")
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

    @commands.command()
    async def shop(self, ctx):
        """
        🎃 Lệnh .shop – mở cửa hàng bán cần, mồi, lưỡi
        Embed + Select menu cực đẹp theme Halloween
        """
        if ctx.channel.id != config.ALLOWED_CHANNEL:
            return await ctx.send("⚰️ Bạn không thể mở chợ ma ở đây!")

        user = self.get_user(ctx.author.id)

        # Gộp tất cả item bán được
        all_items = []

        for rod in self.rods:
            if "Halloween" in rod["name"]:
                continue
            all_items.append({
                "id": rod["id"],
                "name": rod["name"],
                "type": "rod",
                "price": rod["price"],
                "desc": rod.get("description", "Một cây cần bí ẩn...")
            })

        for bait in self.items.get("bait", []):
            all_items.append({
                "id": bait["id"],
                "name": bait["name"],
                "type": "bait",
                "price": bait["price"],
                "desc": f"🪱 Bonus bắt cá: +{bait['bonus_catch_rate']}%"
            })

        for hook in self.items.get("hook", []):
            all_items.append({
                "id": hook["id"],
                "name": hook["name"],
                "type": "hook",
                "price": hook["price"],
                "desc": f"🪝 Giảm gãy cần: -{hook['reduce_break_chance']}%"
            })

        embed = discord.Embed(
            title="🏪 🎃 Chợ Phép Thuật Halloween",
            description=(
                "🕯️ \"Chào mừng đến với chợ hắc ám nơi mọi giao dịch đều chứa lời nguyền...\"\n"
                "⚰️ Chọn vật phẩm muốn mua bên dưới."
            ),
            color=0xeb984e
        )

        for item in all_items:
            emoji = "🎣" if item["type"] == "rod" else ("🪱" if item["type"] == "bait" else "🪝")
            embed.add_field(
                name=f"{emoji} {item['name']} – {item['price']}💰",
                value=item["desc"],
                inline=False
            )

        embed.set_footer(text="🎃 Hãy khôn ngoan khi mua – mọi món đồ đều mang linh hồn!")

        options = [
            discord.SelectOption(
                label=f"{item['name']} – {item['price']}💰",
                value=item["id"]
            ) for item in all_items
        ]

        view = View(timeout=90)

        select = Select(
            placeholder="🛒 Chọn vật phẩm muốn mua",
            options=options
        )

        async def select_callback(interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("⚰️ Đây không phải chợ của ngươi!", ephemeral=True)
                return

            selected_id = select.values[0]
            item = next((i for i in all_items if i["id"] == selected_id), None)

            if not item:
                await interaction.response.send_message("💀 Món đồ này biến mất trong sương mù!", ephemeral=True)
                return

            if user["coins"] < item["price"]:
                await interaction.response.send_message(
                    f"💰 Ngươi không đủ xu! ({user['coins']} / {item['price']})", ephemeral=True)
                return

            user["coins"] -= item["price"]

            if item["type"] == "rod":
                if item["name"] not in user["rods_owned"]:
                    user["rods_owned"].append(item["name"])
                await interaction.response.send_message(
                    f"🎣 Ngươi đã mua **{item['name']}**! Số xu còn lại: {user['coins']}", ephemeral=True)
            elif item["type"] == "bait":
                user["equipped_bait"] = item["name"]
                await interaction.response.send_message(
                    f"🪱 Đã mua và trang bị ngay **{item['name']}**!", ephemeral=True)
            elif item["type"] == "hook":
                user["equipped_hook"] = item["name"]
                await interaction.response.send_message(
                    f"🪝 Đã mua và trang bị ngay **{item['name']}**!", ephemeral=True)

            save_json("users.json", self.users)

        select.callback = select_callback
        view.add_item(select)

        await ctx.send(embed=embed, view=view)

# 📌 BẮT BUỘC CHO DISCORD.PY 2.X
async def setup(bot):
    await bot.add_cog(Shop(bot))