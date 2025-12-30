import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Default delete time (seconds)
delete_time = 60  # 1 minute


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")


# 🔒 Admin-only slash command
@bot.tree.command(
    name="set_delete_time",
    description="Set auto-delete time for mp3/wav files (1–300 seconds)"
)
@app_commands.checks.has_permissions(administrator=True)
async def set_delete_time(interaction: discord.Interaction, seconds: int):
    global delete_time

    if seconds < 1 or seconds > 300:
        await interaction.response.send_message(
            "❌ Time must be between **1 and 300 seconds**.",
            ephemeral=True
        )
        return

    delete_time = seconds
    await interaction.response.send_message(
        f"✅ Audio files will now be deleted after **{delete_time} seconds**.",
        ephemeral=True
    )


@set_delete_time.error
async def set_delete_time_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ Only **administrators** can use this command.",
            ephemeral=True
        )


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    for attachment in message.attachments:
        filename = attachment.filename.lower()
        if filename.endswith(".mp3") or filename.endswith(".wav"):
            await asyncio.sleep(delete_time)
            try:
                await message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

    await bot.process_commands(message)


# 🔑 Railway uses environment variables
bot.run(os.getenv("DISCORD_TOKEN"))
