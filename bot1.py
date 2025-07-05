# bot.py
import discord
from discord.ext import commands
import asyncio
import config

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=".", 
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f"🎃🕯️ BOT ĐÃ SỐNG DẬY: {bot.user}!")
    await bot.change_presence(
        activity=discord.Game(name="🎣 Săn cá ma quái | .hoso để xem hồ sơ")
    )

extensions = [
    "cogs.profile",
    "cogs.shop",
    "cogs.fishing",
    "cogs.map",
    "cogs.quest",
    "cogs.admin",
    "cogs.start",
    "cogs.leaderboard"
]

async def main():
    async with bot:
        for ext in extensions:
            print(f"🧙‍♂️ Đang triệu hồi phép thuật: {ext}")
            await bot.load_extension(ext)
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())