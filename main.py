import os
import requests
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ButtonStyle
from nextcord.ui import Button, View

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DA_TOKEN = os.getenv("DA_ACCESS_TOKEN")

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === DeviantArt NSFW Fetcher ===
async def fetch_deviantart_images(tag, limit=10):
    try:
        url = (
            f"https://www.deviantart.com/api/v1/oauth2/browse/tags"
            f"?tag={tag}&limit={limit}&access_token={DA_TOKEN}&mature_content=true"
        )
        r = requests.get(url, timeout=10)
        if r.ok:
            data = r.json()
            return [
                item["content"]["src"]
                for item in data.get("results", [])
                if "content" in item and "src" in item["content"]
                and item.get("is_mature", False)
            ]
    except Exception as e:
        print(f"[DEBUG] DeviantArt fetch error: {e}")
    return []

# === Danbooru NSFW Fetcher ===
async def fetch_danbooru_images(tag, limit=10):
    try:
        url = f"https://danbooru.donmai.us/posts.json?tags={tag}+rating:explicit&limit={limit}"
        r = requests.get(url, timeout=10)
        if r.ok:
            data = r.json()
            return [
                post.get("file_url")
                for post in data
                if post.get("file_url", "").endswith((".jpg", ".png", ".jpeg", ".gif"))
            ]
    except Exception as e:
        print(f"[DEBUG] Danbooru fetch error: {e}")
    return []

# === Interactive Image Viewer with Back/Next ===
class ImageView(View):
    def __init__(self, tag, images, user_id):
        super().__init__(timeout=120)
        self.images = images
        self.index = 0
        self.tag = tag
        self.user_id = user_id

        self.next_button = Button(label="🔁 Next", style=ButtonStyle.primary)
        self.prev_button = Button(label="🔙 Back", style=ButtonStyle.secondary)

        self.next_button.callback = self.next_image
        self.prev_button.callback = self.prev_image

        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    async def next_image(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ Only you can use these buttons.", ephemeral=True)
            return
        self.index = (self.index + 1) % len(self.images)
        await interaction.response.edit_message(content=self.images[self.index], view=self)

    async def prev_image(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ Only you can use these buttons.", ephemeral=True)
            return
        self.index = (self.index - 1) % len(self.images)
        await interaction.response.edit_message(content=self.images[self.index], view=self)

# === Slash Command ===
@bot.slash_command(name="nsfw", description="Get NSFW images by tag or character")
async def nsfw(
    interaction: Interaction,
    tag: str = SlashOption(name="tag", description="Character or tag (e.g. futa, 2B, Rias)", required=True)
):
    await interaction.response.defer()
    images = await fetch_deviantart_images(tag)
    if not images:
        images = await fetch_danbooru_images(tag)

    if images:
        view = ImageView(tag, images, interaction.user.id)
        await interaction.followup.send(content=images[0], view=view)
    else:
        await interaction.followup.send("❌ No NSFW images found on DeviantArt or Danbooru.")

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
