import os
import json
import requests
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ButtonStyle
from nextcord.ui import Button, View

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DA_TOKEN = os.getenv("DA_ACCESS_TOKEN")  # DeviantArt API OAuth2 token

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_sessions = {}

# === Image Fetchers ===
async def fetch_images(tag, limit=5):
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
                images = [
                    p.get("file_url") for p in data
                    if p.get("file_url") and p.get("file_url").endswith((".jpg", ".png", ".jpeg", ".gif"))
                ]
                if images:
                    return images
        except Exception as e:
            print(f"[DEBUG] Error fetching from {url} → {e}")
    return []

async def fetch_deviantart_images(tag, limit=5):
    try:
        url = f"https://www.deviantart.com/api/v1/oauth2/browse/tags?tag={tag}&limit={limit}&access_token={DA_TOKEN}&mature_content=true"
        r = requests.get(url, timeout=10)
        if r.ok:
            data = r.json()
            images = [
                item["content"]["src"]
                for item in data.get("results", [])
                if "content" in item and "src" in item["content"]
            ]
            return images
    except Exception as e:
        print(f"[DEBUG] DeviantArt fetch error: {e}")
    return []

# === Button View ===
class ImageView(View):
    def __init__(self, tag, images, user_id):
        super().__init__(timeout=60)
        self.images = images
        self.index = 0
        self.tag = tag
        self.user_id = user_id
        self.next_button = Button(label="🔁 Next", style=ButtonStyle.primary)
        self.next_button.callback = self.next_image
        self.add_item(self.next_button)

    async def next_image(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ Only the original requester can use this.", ephemeral=True)
            return
        self.index = (self.index + 1) % len(self.images)
        await interaction.response.edit_message(content=self.images[self.index], view=self)

# === Slash Command ===
@bot.slash_command(name="nsfw", description="Search NSFW images by tag")
async def nsfw(
    interaction: Interaction,
    tag: str = SlashOption(name="tag", description="Enter tag like 'elf', 'futa', 'maid'", required=True)
):
    await interaction.response.defer()
    images = await fetch_images(tag)
    if not images:
        images = await fetch_deviantart_images(tag)
    if images:
        user_sessions[interaction.user.id] = tag
        view = ImageView(tag=tag, images=images, user_id=interaction.user.id)
        await interaction.followup.send(content=images[0], view=view)
    else:
        await interaction.followup.send("❌ No images found for that tag.")

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
