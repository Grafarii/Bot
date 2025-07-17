
import random
import requests
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

TOKEN = "8044715557:AAGdxBxX1--A5efKqTsRSB7larhMD8efALk"

user_query = {}
user_images = {}

MAIN_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔍 Search NSFW by Character", callback_data="search")],
    [InlineKeyboardButton("🎲 Random NSFW", callback_data="random")],
    [InlineKeyboardButton("ℹ️ About", callback_data="about")]
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Welcome to the Ultimate NSFW Bot!
Choose an option below:",
        reply_markup=MAIN_MENU
    )

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "search":
        await query.edit_message_text("✏️ Please send me the name of a character to search.")
    elif query.data == "random":
        await send_random_image(query.message.chat.id, context)
    elif query.data == "about":
        await query.edit_message_text(
            "🤖 This bot fetches NSFW anime images using Rule34.xxx.

"
            "Created with ❤️ by AI. Hosted 24/7 on Railway.

"
            "Use responsibly. Type /start to return to menu."
        )

async def receive_character_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    term = update.message.text.strip()

    images = fetch_rule34_images(term)
    if not images:
        await update.message.reply_text("❌ No images found. Try another name.")
        return

    user_query[user_id] = term
    user_images[user_id] = images

    keyboard = [[InlineKeyboardButton("➡️ Next Image", callback_data="next")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(photo=images[0], caption=f"🔞 Results for: {term}", reply_markup=reply_markup)

async def next_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    images = user_images.get(user_id, [])

    if images:
        image = random.choice(images)
        keyboard = [[InlineKeyboardButton("➡️ Next Image", callback_data="next")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=image, reply_markup=reply_markup)
    else:
        await query.message.reply_text("⚠️ No history found. Please search a character first.")

async def send_random_image(chat_id, context):
    random_tags = ["asuna", "hinata", "mikasa", "zero_two", "yor_forger"]
    term = random.choice(random_tags)
    images = fetch_rule34_images(term)

    if images:
        image = random.choice(images)
        await context.bot.send_photo(chat_id=chat_id, photo=image, caption=f"🎲 Random: {term}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="❌ No random images found.")

def fetch_rule34_images(term):
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit=20&tags={term.replace(' ', '_')}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return [item["file_url"] for item in data if item.get("file_url", "").endswith((".jpg", ".png", ".jpeg", ".webp"))]
    except:
        return []

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_menu_selection))
app.add_handler(CallbackQueryHandler(next_image, pattern="^next$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_character_name))

if __name__ == "__main__":
    print("💎 Premium NSFW Bot is running...")
    app.run_polling()
