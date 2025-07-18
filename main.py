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

# === DeviantArt Image Fetcher ===
async def fetch_deviantart_best_images(tag, limit=10):
    try:
        query = tag.replace(" ", "+")
        url = (
            f"https://www.deviantart.com/api/v1/oauth2/browse/newest"
            f"?q={query}&limit={limit}&access_token={DA_TOKEN}&mature_content=true"
        )
        r = requests.get(url, timeout=10)
        if r.ok:
            data = r.json()
            images = [
                item["content"]["src"]
                for item in data.get("results", [])
                if "content" in item and "src" in item["content"]
                and item.get("is_mature", False)
            ]
            return images
    except Exception as e:
        print(f"[DEBUG] DeviantArt fetch error: {e}")
    return []

# === View With Button ===
class ImageView(View):
    def __init__(self, tag, images, user_id):
        super().__init__(timeout=60)
        self.images = images
        self.index = 0
        self.tag = tag
        self.user_id = user_id
        next_btn = Button(label="🔁 Next", style=ButtonStyle.primary)
        next_btn.callback = self.next_image
        self.add_item(next_btn)

    async def next_image(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ Only the original requester can use this.", ephemeral=True)
            return
        self.index = (self.index + 1) % len(self.images)
        await interaction.response.edit_message(content=self.images[self.index], view=self)

# === Slash Command ===
@bot.slash_command(name="nsfw", description="Get NSFW DeviantArt images by tag or character name")
async def nsfw(
    interaction: Interaction,
    tag: str = SlashOption(name="tag", description="Enter a tag or character name", required=True)
):
    await interaction.response.defer()
    images = await fetch_deviantart_best_images(tag)
    if images:
        view = ImageView(tag, images, interaction.user.id)
        await interaction.followup.send(content=images[0], view=view)
    else:
        await interaction.followup.send("❌ No images found for that tag on DeviantArt.")

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
