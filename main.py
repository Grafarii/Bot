# main.py – LustFetchBot (no .env version)
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor

API_TOKEN = '8044715557:AAGdxBxX1--A5efKqTsRSB7larhMD8efALk'
ADMINS = [123456789]
ADMIN_UNLOCK_CODE = 'UNLOCKGODS666'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

def fetch_from_danbooru(tags, limit=3):
    url = f"https://danbooru.donmai.us/posts.json?tags={tags}+rating:explicit&limit={limit}"
    r = requests.get(url)
    return [post['file_url'] for post in r.json() if 'file_url' in post] if r.ok else []

def fetch_from_gelbooru(tags, limit=3):
    url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tags}"
    r = requests.get(url)
    return [post['file_url'] for post in r.json() if 'file_url' in post] if r.ok else []

def fetch_from_rule34(tags, limit=3):
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tags}"
    r = requests.get(url)
    return [post['file_url'] for post in r.json() if 'file_url' in post] if r.ok else []

def fetch_images(tags, limit=3):
    return (
        fetch_from_danbooru(tags, limit) or
        fetch_from_gelbooru(tags, limit) or
        fetch_from_rule34(tags, limit)
    )

premium_users = set()
admin_unlocked_users = set()
user_preferences = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Search Character 🔍", switch_inline_query_current_chat=""),
        InlineKeyboardButton("Random Tag 🎲", callback_data="random_menu"),
        InlineKeyboardButton("Become Premium 💎", callback_data="premium")
    )
    if message.from_user.id in ADMINS:
        kb.add(InlineKeyboardButton("🔐 Admin Unlock", callback_data="admin_unlock"))
    await message.answer("👋 *Welcome to LustFetchBot!*

Type `/character 2b` or `/random elf` to start.", reply_markup=kb, parse_mode="Markdown")

@dp.message_handler(commands=['character'])
async def character(message: types.Message):
    uid = message.from_user.id
    if len(message.text.split()) < 2:
        return await message.reply("Usage: /character [name]")
    name = '_'.join(message.text.split()[1:])
    await message.reply(f"🔎 Searching for `{name}`...", parse_mode="Markdown")
    limit = 5 if uid in premium_users or uid in admin_unlocked_users else 2
    images = fetch_images(name, limit)
    if not images:
        return await message.reply("❌ No results found.")
    for img in images:
        await bot.send_photo(chat_id=uid, photo=img)

@dp.callback_query_handler(lambda c: c.data == "premium")
async def premium(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id,
        "💎 *Premium Includes:*
- Unlimited images
- HD content
- Waifu drops

https://yourpaymentlink.com", parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "admin_unlock")
async def admin_unlock_prompt(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, "🔐 Send the admin code to unlock full features:")

@dp.message_handler(lambda m: m.text == ADMIN_UNLOCK_CODE)
async def unlock_code(message: types.Message):
    if message.from_user.id in ADMINS:
        admin_unlocked_users.add(message.from_user.id)
        await message.reply("✅ Full access granted.")
    else:
        await message.reply("⛔ Invalid code.")

@dp.callback_query_handler(lambda c: c.data == "random_menu")
async def random_tags(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=2)
    for tag in ["milf", "elf", "futanari", "tentacle", "maid"]:
        kb.insert(InlineKeyboardButton(tag, callback_data=f"tag_{tag}"))
    await bot.send_message(callback.from_user.id, "🎲 Choose a tag:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("tag_"))
async def tag_fetch(callback: types.CallbackQuery):
    tag = callback.data.split("_")[1]
    images = fetch_images(tag, 1)
    if images:
        await bot.send_photo(chat_id=callback.from_user.id, photo=images[0])
    else:
        await bot.send_message(callback.from_user.id, "❌ No results found.")

@dp.message_handler(commands=['setwaifu'])
async def set_waifu(message: types.Message):
    if len(message.text.split()) < 2:
        return await message.reply("Usage: /setwaifu [name]")
    name = '_'.join(message.text.split()[1:])
    user_preferences[message.from_user.id] = name
    await message.reply(f"💖 Waifu set to `{name}`.", parse_mode="Markdown")

@dp.message_handler(commands=['mywaifu'])
async def my_waifu(message: types.Message):
    name = user_preferences.get(message.from_user.id)
    if not name:
        return await message.reply("Set one using /setwaifu [name].")
    limit = 5 if message.from_user.id in premium_users or message.from_user.id in admin_unlocked_users else 2
    images = fetch_images(name, limit)
    if images:
        for img in images:
            await bot.send_photo(message.chat.id, img)
    else:
        await message.reply("No images found for your waifu.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
