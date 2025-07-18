import os
import requests
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Set this in Railway or your environment

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def fetch_images(tag, limit=1):
    headers = {"User-Agent": "Mozilla/5.0"}
    urls = [
        f"https://danbooru.donmai.us/posts.json?tags={tag}+rating:explicit&limit={limit}",
        f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tag}",
        f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tag}"
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.ok:
                data = r.json()
                images = [p.get("file_url") for p in data if p.get("file_url")]
                if images:
                    return images
        except Exception as e:
            print(f"[DEBUG] Error fetching from {url} → {e}")
    return []

@bot.slash_command(name="nsfw", description="Search NSFW images by tag")
async def nsfw(
    interaction: Interaction,
    tag: str = SlashOption(name="tag", description="Enter a tag like 'elf', 'futa', 'maid'", required=True)
):
    await interaction.response.defer()
    images = await fetch_images(tag)
    if images:
        for img in images:
            await interaction.followup.send(img)
    else:
        await interaction.followup.send("❌ No images found for that tag.")

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
