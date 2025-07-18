# main.py – Fixed Discord Bot with Slash Commands and NSFW Channel Check
import os
import requests
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Fetch from APIs
async def fetch_from_danbooru(tags, limit=1):
    url = f"https://danbooru.donmai.us/posts.json?tags={tags}+rating:explicit&limit={limit}"
    r = requests.get(url)
    return [p['file_url'] for p in r.json() if 'file_url' in p] if r.ok else []

async def fetch_from_gelbooru(tags, limit=1):
    url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tags}"
    r = requests.get(url)
    return [p['file_url'] for p in r.json() if 'file_url' in p] if r.ok else []

async def fetch_from_rule34(tags, limit=1):
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tags}"
    r = requests.get(url)
    return [p['file_url'] for p in r.json() if 'file_url' in p] if r.ok else []

async def fetch_images(tag, limit=1):
    return (
        await fetch_from_danbooru(tag, limit) or
        await fetch_from_gelbooru(tag, limit) or
        await fetch_from_rule34(tag, limit)
    )

# Slash command
@bot.slash_command(name="nsfw", description="Search NSFW images by tag", guild_ids=[])
async def nsfw(
    interaction: Interaction,
    tag: str = SlashOption(name="tag", description="Search term (e.g. elf, futa, maid)", required=True)
):
    channel = await bot.fetch_channel(interaction.channel_id)
    if not channel.is_nsfw():
        await interaction.response.send_message("⚠️ This command only works in NSFW-marked channels.", ephemeral=True)
        return

    await interaction.response.defer()
    results = await fetch_images(tag)
    if results:
        for img in results:
            await interaction.followup.send(img)
    else:
        await interaction.followup.send("❌ No results found.")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
