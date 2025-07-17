# main.py – Railway-compatible Discord NSFW Bot
import os
import discord
import requests
import asyncio

TOKEN = os.getenv("MTM5NTU0OTQwODU2MDY3Njg4NA.GWtz6d.G7Jn3pCsU-jy2H1wz6x4R5krgYRjbGvkZ2_7hM")
INTENTS = discord.Intents.default()
INTENTS.message_content = True
client = discord.Client(intents=INTENTS)

async def fetch_from_danbooru(tags, limit=1):
    url = f"https://danbooru.donmai.us/posts.json?tags={tags}+rating:explicit&limit={limit}"
    r = requests.get(url)
    return [post['file_url'] for post in r.json() if 'file_url' in post] if r.ok else []

async def fetch_from_gelbooru(tags, limit=1):
    url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tags}"
    r = requests.get(url)
    return [post['file_url'] for post in r.json() if 'file_url' in post] if r.ok else []

async def fetch_from_rule34(tags, limit=1):
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tags}"
    r = requests.get(url)
    return [post['file_url'] for post in r.json() if 'file_url' in post] if r.ok else []

async def fetch_images(tag, limit=1):
    return (
        await fetch_from_danbooru(tag, limit) or
        await fetch_from_gelbooru(tag, limit) or
        await fetch_from_rule34(tag, limit)
    )

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.channel.is_nsfw():
        return await message.channel.send("⚠️ NSFW content is only allowed in NSFW-marked channels.")

    if message.content.startswith("!nsfw "):
        tag = message.content[6:].strip().replace(" ", "_")
        await message.channel.send(f"🔍 Searching for `{tag}`...")
        images = await fetch_images(tag)
        if images:
            for img in images:
                await message.channel.send(img)
        else:
            await message.channel.send("❌ No results found.")

client.run(TOKEN)
