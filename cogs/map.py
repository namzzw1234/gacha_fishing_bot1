# cogs/map.py
# 🗺️ ~ Vùng biển ma quái để săn cá Halloween ~ 🎃

import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from utils.database import load_json, save_json
import config

class Map(commands.Cog):
    """📜 Cog quản lý lệnh .map – chọn vùng biển ma quái."""

    def __init__(self, bot):
        self.bot = bot
        self.users = load_json("users.json")
        self.maps = load_json("maps.json")

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
    async def map(self, ctx):
        """
        🗺️ Lệnh .map – chọn vùng biển để câu cá
        Có giới hạn level
        Giao diện Halloween ngầu
        """
        if ctx.channel.id != config.ALLOWED_CHANNEL:
            return await ctx.send("⚰️ Không thể triệu hồi bản đồ ở đây!")

        user = self.get_user(ctx.author.id)
        level = user.get("level", 1)

        class MapView(View):
            def __init__(self, maps_list, current_index=0):
                super().__init__(timeout=120)
                self.maps_list = maps_list
                self.index = current_index
                self.message = None
                self.update_buttons()

            def update_buttons(self):
                self.clear_items()
                # Trang trước
                self.prev_button = Button(label="⬅️ Trang trước", style=discord.ButtonStyle.secondary)
                self.prev_button.disabled = self.index == 0
                self.prev_button.callback = self.prev_page
                self.add_item(self.prev_button)

                # Trang sau
                self.next_button = Button(label="Trang sau ➡️", style=discord.ButtonStyle.secondary)
                self.next_button.disabled = self.index == len(self.maps_list) - 1
                self.next_button.callback = self.next_page
                self.add_item(self.next_button)

                # Nút chọn
                current_map = self.maps_list[self.index]
                can_enter = level >= current_map.get("min_level", 1)
                self.select_button = Button(
                    label=f"Chọn {current_map['name']}",
                    style=discord.ButtonStyle.success if can_enter else discord.ButtonStyle.danger,
                    disabled=not can_enter,
                )
                self.select_button.callback = self.select_map
                self.add_item(self.select_button)

            async def prev_page(self, interaction):
                if self.index > 0:
                    self.index -= 1
                    await self.refresh(interaction)

            async def next_page(self, interaction):
                if self.index < len(self.maps_list) - 1:
                    self.index += 1
                    await self.refresh(interaction)

            async def select_map(self, interaction):
                selected_map = self.maps_list[self.index]
                if level < selected_map.get("min_level", 1):
                    await interaction.response.send_message(
                        "⚰️ Ngươi chưa đủ sức mạnh để vào vùng biển ma quái này!", ephemeral=True)
                    return

                user["map"] = selected_map["id"]
                save_json("users.json", self.users)
                await interaction.response.send_message(
                    f"✅ Ngươi đã chọn **{selected_map['name']}** – chuẩn bị cho chuyến câu cá ma quái! 🎃",
                    ephemeral=True
                )
                await self.message.delete()
                self.stop()

            async def refresh(self, interaction):
                current_map = self.maps_list[self.index]
                desc = (
                    f"🗺️ **Mô tả:** {current_map['description']}\n"
                    f"🪄 **Cấp yêu cầu:** {current_map['min_level']}\n"
                    f"✨ **EXP bonus:** {current_map['exp_bonus']}%\n"
                    f"💀 **Tỉ lệ xuất hiện cá hiếm:**\n"
                    f" - Thường: {current_map['rarity_rates']['common']}%\n"
                    f" - Hiếm: {current_map['rarity_rates']['rare']}%\n"
                    f" - Huyền thoại: {current_map['rarity_rates']['legendary']}%\n\n"
                    f"🕯️ Một vùng biển đen tối chờ ngươi khám phá..."
                )
                embed = discord.Embed(
                    title=f"🌊 Vùng biển: {current_map['name']}",
                    description=desc,
                    color=0xeb984e,
                )
                embed.set_footer(
                    text="🎃 Chỉ những thợ câu gan dạ mới dám đi sâu hơn..."
                )

                if current_map.get("image") and os.path.exists(current_map["image"]):
                    file = discord.File(current_map["image"], filename="map.png")
                    if self.message:
                        await self.message.delete()
                    self.message = await interaction.channel.send(embed=embed, file=file, view=self)
                else:
                    if self.message:
                        await self.message.delete()
                    self.message = await interaction.channel.send(embed=embed, view=self)

        # Gửi trang đầu tiên
        view = MapView(self.maps)
        first_map = self.maps[0]
        desc = (
            f"🗺️ **Mô tả:** {first_map['description']}\n"
            f"🪄 **Cấp yêu cầu:** {first_map['min_level']}\n"
            f"✨ **EXP bonus:** {first_map['exp_bonus']}%\n"
            f"💀 **Tỉ lệ xuất hiện cá hiếm:**\n"
            f" - Thường: {first_map['rarity_rates']['common']}%\n"
            f" - Hiếm: {first_map['rarity_rates']['rare']}%\n"
            f" - Huyền thoại: {first_map['rarity_rates']['legendary']}%\n\n"
            f"🕯️ Một vùng biển đen tối chờ ngươi khám phá..."
        )
        embed = discord.Embed(
            title=f"🌊 Vùng biển: {first_map['name']}",
            description=desc,
            color=0xeb984e,
        )
        embed.set_footer(
            text="🎃 Chỉ những thợ câu gan dạ mới dám đi sâu hơn..."
        )

        if first_map.get("image") and os.path.exists(first_map["image"]):
            file = discord.File(first_map["image"], filename="map.png")
            view.message = await ctx.send(embed=embed, file=file, view=view)
        else:
            view.message = await ctx.send(embed=embed, view=view)

# 📌 BẮT BUỘC CHO DISCORD.PY 2.X
async def setup(bot):
    await bot.add_cog(Map(bot))