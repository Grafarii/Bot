import os
import requests
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, ButtonStyle
from nextcord.ui import Button, View

# Bot Token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Danbooru NSFW-only Fetcher ===
async def fetch_danbooru_images(tag, limit=10):
    try:
        url = f"https://danbooru.donmai.us/posts.json?tags={tag}+rating:explicit&limit={limit}"
        r = requests.get(url, timeout=10)
        if r.ok:
            data = r.json()
            return [
                post["file_url"]
                for post in data
                if post.get("file_url", "").endswith((".jpg", ".jpeg", ".png", ".gif"))
            ]
    except Exception as e:
        print(f"[DEBUG] Danbooru error: {e}")
    return []

# === Image Viewer with Back/Next Buttons ===
class ImageView(View):
    def __init__(self, tag, images, user_id):
        super().__init__(timeout=120)
        self.images = images
        self.index = 0
        self.tag = tag
        self.user_id = user_id

        next_btn = Button(label="🔁 Next", style=ButtonStyle.primary)
        prev_btn = Button(label="🔙 Back", style=ButtonStyle.secondary)
        next_btn.callback = self.next_image
        prev_btn.callback = self.prev_image
        self.add_item(prev_btn)
        self.add_item(next_btn)

    async def next_image(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ Only you can use this.", ephemeral=True)
            return
        self.index = (self.index + 1) % len(self.images)
        await interaction.response.edit_message(content=self.images[self.index], view=self)

    async def prev_image(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ Only you can use this.", ephemeral=True)
            return
        self.index = (self.index - 1) % len(self.images)
        await interaction.response.edit_message(content=self.images[self.index], view=self)

# === Slash Command ===
@bot.slash_command(name="nsfw", description="Get NSFW images from Danbooru by tag or character")
async def nsfw(
    interaction: Interaction,
    tag: str = SlashOption(name="tag", description="Example: futanari, 2B, Makima", required=True)
):
    await interaction.response.defer()
    images = await fetch_danbooru_images(tag)
    if images:
        view = ImageView(tag, images, interaction.user.id)
        await interaction.followup.send(content=images[0], view=view)
    else:
        await interaction.followup.send("❌ No explicit images found for that tag on Danbooru.")

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
