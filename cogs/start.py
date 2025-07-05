# cogs/start.py
# 🧙‍♂️ ~ Nghi thức triệu hồi nhân vật Halloween ~ 🎃

import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from utils.database import load_json, save_json
import config

class Start(commands.Cog):
    """📜 Cog quản lý lệnh .batdau – chọn nhân vật."""

    def __init__(self, bot):
        self.bot = bot
        self.users = load_json("users.json")
        self.characters = load_json("characters.json")

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
    async def batdau(self, ctx):
        """
        🧙‍♂️ Lệnh .batdau – chọn nhân vật với giao diện Halloween
        """
        if ctx.channel.id != config.ALLOWED_CHANNEL:
            return await ctx.send("⚰️ Không thể làm nghi thức chọn nhân vật ở đây!")

        user = self.get_user(ctx.author.id)
        if user.get("character"):
            return await ctx.send(
                "🕯️ Ngươi đã có nhân vật rồi! Số phận không thể chọn lại."
            )

        class CharacterView(View):
            def __init__(self, chars, current_index=0):
                super().__init__(timeout=120)
                self.chars = chars
                self.index = current_index
                self.message = None
                self.update_buttons()

            def update_buttons(self):
                self.clear_items()
                self.prev_button = Button(label="⬅️ Trang trước", style=discord.ButtonStyle.secondary)
                self.prev_button.disabled = self.index == 0
                self.prev_button.callback = self.prev_page
                self.add_item(self.prev_button)

                self.next_button = Button(label="Trang sau ➡️", style=discord.ButtonStyle.secondary)
                self.next_button.disabled = self.index == len(self.chars) - 1
                self.next_button.callback = self.next_page
                self.add_item(self.next_button)

                self.select_button = Button(
                    label=f"✅ Chọn {self.chars[self.index]['name']}",
                    style=discord.ButtonStyle.success
                )
                self.select_button.callback = self.select_character
                self.add_item(self.select_button)

            async def prev_page(self, interaction):
                if self.index > 0:
                    self.index -= 1
                    await self.refresh(interaction)

            async def next_page(self, interaction):
                if self.index < len(self.chars) - 1:
                    self.index += 1
                    await self.refresh(interaction)

            async def select_character(self, interaction):
                selected = self.chars[self.index]
                user["character"] = selected["id"]
                save_json("users.json", self.users)

                await interaction.response.send_message(
                    f"✅ Ngươi đã chọn **{selected['name']}**! "
                    f"🕯️ Kỹ năng đặc biệt: {selected['skill']}\n"
                    f"🎃 Hãy chuẩn bị cho đêm săn cá ma quái!",
                    ephemeral=True
                )
                await self.message.delete()
                self.stop()

            async def refresh(self, interaction):
                char = self.chars[self.index]
                desc = (
                    f"📜 **Mô tả:** {char['description']}\n"
                    f"✨ **Kỹ năng:** {char['skill']}\n\n"
                    f"🕯️ Hãy chọn thật cẩn thận – mỗi nhân vật mang theo một lời nguyền riêng..."
                )

                embed = discord.Embed(
                    title=f"🧙‍♂️ Nhân vật: {char['name']}",
                    description=desc,
                    color=0xeb984e,
                )
                embed.set_footer(
                    text="🎃 Một lựa chọn – một số phận..."
                )

                if char.get("image") and os.path.exists(char["image"]):
                    file = discord.File(char["image"], filename="character.png")
                    if self.message:
                        await self.message.delete()
                    self.message = await interaction.channel.send(embed=embed, file=file, view=self)
                else:
                    if self.message:
                        await self.message.delete()
                    self.message = await interaction.channel.send(embed=embed, view=self)

        view = CharacterView(self.characters)
        first = self.characters[0]
        desc = (
            f"📜 **Mô tả:** {first['description']}\n"
            f"✨ **Kỹ năng:** {first['skill']}\n\n"
            f"🕯️ Hãy chọn thật cẩn thận – mỗi nhân vật mang theo một lời nguyền riêng..."
        )
        embed = discord.Embed(
            title=f"🧙‍♂️ Nhân vật: {first['name']}",
            description=desc,
            color=0xeb984e,
        )
        embed.set_footer(
            text="🎃 Một lựa chọn – một số phận..."
        )

        if first.get("image") and os.path.exists(first["image"]):
            file = discord.File(first["image"], filename="character.png")
            view.message = await ctx.send(embed=embed, file=file, view=view)
        else:
            view.message = await ctx.send(embed=embed, view=view)

# 📌 BẮT BUỘC CHO DISCORD.PY 2.X
async def setup(bot):
    await bot.add_cog(Start(bot))