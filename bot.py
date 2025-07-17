LustFetchBot – Ultimate NSFW Telegram Bot with Multi-API, Premium, Admin Unlock, and Enhanced UX

Built in Python (Aiogram) – Production-Ready Version

from aiogram import Bot, Dispatcher, types, executor import requests from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton import logging

API_TOKEN = '8044715557:AAGdxBxX1--A5efKqTsRSB7larhMD8efALk' ADMINS = [123456789]  # Replace with real admin user IDs ADMIN_UNLOCK_CODE = "UNLOCKGODS666"

bot = Bot(token=API_TOKEN) dp = Dispatcher(bot) logging.basicConfig(level=logging.INFO)

--- UTILITIES ---

def fetch_from_danbooru(tags, limit=3): url = f"https://danbooru.donmai.us/posts.json?tags={tags}+rating:explicit&limit={limit}" r = requests.get(url) if r.ok: return [post['file_url'] for post in r.json() if 'file_url' in post] return []

def fetch_from_gelbooru(tags, limit=3): url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tags}" r = requests.get(url) if r.ok: return [post['file_url'] for post in r.json() if 'file_url' in post] return []

def fetch_from_rule34(tags, limit=3): url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&tags={tags}" r = requests.get(url) if r.ok: return [post['file_url'] for post in r.json() if 'file_url' in post] return []

def fetch_images(tags, limit=3): results = fetch_from_danbooru(tags, limit) if not results: results = fetch_from_gelbooru(tags, limit) if not results: results = fetch_from_rule34(tags, limit) return results

--- USER DATABASE MOCK ---

premium_users = set() admin_unlocked_users = set() user_preferences = {}  # Stores saved waifus

--- START ---

@dp.message_handler(commands=['start']) async def start_cmd(message: types.Message): keyboard = InlineKeyboardMarkup(row_width=2) keyboard.add( InlineKeyboardButton("Search Character 🔍", switch_inline_query_current_chat=""), InlineKeyboardButton("Random Tag 🎲", callback_data="random_menu"), InlineKeyboardButton("Become Premium 💎", callback_data="premium") ) if message.from_user.id in ADMINS: keyboard.add(InlineKeyboardButton("🔐 Admin Unlock", callback_data="admin_unlock"))

await message.answer(
    "Welcome to *LustFetchBot* – your AI-powered NSFW image bot.\n\nUse the menu below or type `/character [name]` or `/random [tag]`.",
    reply_markup=keyboard, parse_mode="Markdown")

--- CHARACTER SEARCH ---

@dp.message_handler(commands=['character']) async def character_cmd(message: types.Message): user_id = message.from_user.id if len(message.text.split()) < 2: await message.reply("Usage: /character [name]") return name = '_'.join(message.text.split()[1:]) await message.reply(f"Searching for {name}...", parse_mode="Markdown")

limit = 5 if user_id in premium_users or user_id in admin_unlocked_users else 2
images = fetch_images(name, limit=limit)
if not images:
    await message.reply("No results found. Try a different character or spelling.")
    return

for img in images:
    await bot.send_photo(chat_id=message.chat.id, photo=img)

--- PREMIUM BUTTON ---

@dp.callback_query_handler(lambda c: c.data == "premium") async def premium_callback(callback_query: types.CallbackQuery): await bot.answer_callback_query(callback_query.id) await bot.send_message(callback_query.from_user.id, "💎 Premium Includes:\n- Unlimited searches\n- 5+ results per fetch\n- HD-only toggle\n- Daily waifu drop\n\nUpgrade now: https://yourpaymentlink.com", parse_mode="Markdown")

--- ADMIN UNLOCK ---

@dp.callback_query_handler(lambda c: c.data == "admin_unlock") async def admin_unlock_button(callback_query: types.CallbackQuery): await bot.answer_callback_query(callback_query.id) await bot.send_message(callback_query.from_user.id, "Send the secret admin unlock code:")

@dp.message_handler(lambda m: m.text == ADMIN_UNLOCK_CODE) async def admin_unlock_code_handler(message: types.Message): if message.from_user.id in ADMINS: admin_unlocked_users.add(message.from_user.id) await message.reply("✅ Admin mode enabled. Full features unlocked.") else: await message.reply("⛔ You're not allowed to use this code.")

--- RANDOM TAG FETCH ---

@dp.callback_query_handler(lambda c: c.data == "random_menu") async def random_menu_callback(callback_query: types.CallbackQuery): keyboard = InlineKeyboardMarkup(row_width=2) for tag in ["milf", "futanari", "bondage", "elf", "schoolgirl", "maid"]: keyboard.insert(InlineKeyboardButton(tag, callback_data=f"tag_{tag}")) await bot.send_message(callback_query.from_user.id, "🎲 Pick a tag to fetch a random image:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("tag_")) async def tag_callback(callback_query: types.CallbackQuery): tag = callback_query.data.split("_")[1] images = fetch_images(tag, limit=1) if images: await bot.send_photo(chat_id=callback_query.from_user.id, photo=images[0]) else: await bot.send_message(callback_query.from_user.id, "No results found for that tag.")

--- DAILY WAIFU DROP (For Premium Users) ---

@dp.message_handler(commands=['mywaifu']) async def waifu_cmd(message: types.Message): uid = message.from_user.id waifu = user_preferences.get(uid) if not waifu: await message.reply("❌ No waifu set. Use /setwaifu [name] to save one.") return limit = 5 if uid in premium_users or uid in admin_unlocked_users else 2 images = fetch_images(waifu, limit=limit) if images: for img in images: await bot.send_photo(message.chat.id, img) else: await message.reply("No images found for your waifu today.")

@dp.message_handler(commands=['setwaifu']) async def set_waifu_cmd(message: types.Message): if len(message.text.split()) < 2: await message.reply("Usage: /setwaifu [character_name]") return name = '_'.join(message.text.split()[1:]) user_preferences[message.from_user.id] = name await message.reply(f"💖 Your waifu has been set to {name}! Use /mywaifu anytime.", parse_mode="Markdown")

--- RUN ---

if name == 'main': executor.start_polling(dp, skip_updates=True)

