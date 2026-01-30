import discord
from discord.ext import commands
from discord import app_commands
import asyncio

TOKEN = "YOUR_BOT_TOKEN_HERE"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------- Settings --------
delete_enabled = True
delete_delay = 60  # default seconds
AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a")

# -------- Ready --------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# -------- Message Listener --------
@bot.event
async def on_message(message: discord.Message):
    global delete_enabled, delete_delay

    if message.author.bot or not delete_enabled:
        return

    # Check ONLY attachments for audio files
    audio_attachments = [
        a for a in message.attachments
        if a.filename.lower().endswith(AUDIO_EXTENSIONS)
    ]

    if not audio_attachments:
        return  # No audio = ignore message completely

    try:
        warning = await message.channel.send(
            f"⚠️ **Notice:** Your audio file(s) will be deleted in **{delete_delay} seconds**."
        )

        await asyncio.sleep(delete_delay)

        await message.delete()
        await warning.delete()

    except (discord.Forbidden, discord.NotFound):
        pass

    await bot.process_commands(message)

# -------- Slash Commands --------
@bot.tree.command(name="setdelay", description="Set delay before audio files are deleted (0–300 seconds)")
@app_commands.describe(seconds="Seconds before deletion")
async def setdelay(interaction: discord.Interaction, seconds: int):
    global delete_delay

    if not 0 <= seconds <= 300:
        await interaction.response.send_message(
            "❌ Please choose a value between **0 and 300 seconds**.",
            ephemeral=True
        )
        return

    delete_delay = seconds
    await interaction.response.send_message(
        f"✅ Audio deletion delay set to **{seconds} seconds**."
    )

@bot.tree.command(name="toggle", description="Enable or disable audio file auto-deletion")
async def toggle(interaction: discord.Interaction):
    global delete_enabled

    delete_enabled = not delete_enabled
    status = "enabled" if delete_enabled else "disabled"

    await interaction.response.send_message(
        f"🔄 Audio auto-deletion is now **{status}**."
    )

bot.run(TOKEN)



