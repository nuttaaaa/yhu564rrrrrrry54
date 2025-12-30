import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Settings (per-bot, simple version)
delete_time = 60
auto_delete_enabled = True


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")


# 🔒 Admin-only: set delete time
@bot.tree.command(
    name="set_delete_time",
    description="Set delete time for mp3/wav files (1–300 seconds)"
)
@app_commands.checks.has_permissions(administrator=True)
async def set_delete_time(interaction: discord.Interaction, seconds: int):
    global delete_time

    if not 1 <= seconds <= 300:
        await interaction.response.send_message(
            "❌ Time must be between **1 and 300 seconds**.",
            ephemeral=True
        )
        return

    delete_time = seconds
    await interaction.response.send_message(
        f"✅ Delete time set to **{delete_time} seconds**.",
        ephemeral=True
    )


# 🔒 Admin-only: enable / disable
@bot.tree.command(
    name="audio_autodelete",
    description="Enable or disable mp3/wav auto deletion"
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(
    state=[
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable")
    ]
)
async def audio_autodelete(
    interaction: discord.Interaction,
    state: app_commands.Choice[str]
):
    global auto_delete_enabled

    auto_delete_enabled = state.value == "enable"

    status = "✅ Enabled" if auto_delete_enabled else "❌ Disabled"
    await interaction.response.send_message(
        f"{status} audio auto-delete.",
        ephemeral=True
    )


# Permission error handler
@bot.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ Only **administrators** can use this command.",
            ephemeral=True
        )


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not auto_delete_enabled:
        return

    for attachment in message.attachments:
        name = attachment.filename.lower()
        if name.endswith(".mp3") or name.endswith(".wav"):
            await asyncio.sleep(delete_time)
            try:
                await message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

    await bot.process_commands(message)


bot.run(os.getenv("DISCORD_TOKEN"))
