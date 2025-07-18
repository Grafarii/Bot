import os
import requests
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def fetch_images(tag, limit=1):
    urls = [
        f"https://danbooru.donmai.us/posts.json?tags={tag}+rating:explicit&limit={limit}",
        f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tag}",
        f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tag}"
    ]
    for url in urls:
        try:
            r = requests.get(url)
            if r.ok:
                data = r.json()
                return [p["file_url"] for p in data if "file_url" in p]
        except:
            continue
    return []

@bot.slash_command(name="nsfw", description="Search NSFW images by tag", guild_ids=[])
async def nsfw(
    interaction: Interaction,
    tag: str = SlashOption(name="tag", description="Enter tag (e.g. elf, futa, maid)", required=True)
):
    try:
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message("⚠️ Use this in an NSFW channel.", ephemeral=True)
            return
    except:
        await interaction.response.send_message("⚠️ Couldn't verify NSFW status. Use in a proper channel.", ephemeral=True)
        return

    await interaction.response.defer()
    images = await fetch_images(tag)
    if images:
        for img in images:
            await interaction.followup.send(img)
    else:
        await interaction.followup.send("❌ No results found for that tag.")

@bot.event
async def on_ready():
    print(f"✅ Bot is online: {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
