
import random
import requests
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
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
user_history = {}
user_favorites = {}

MAIN_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔍 Search Top NSFW", callback_data="search")],
    [InlineKeyboardButton("🎲 Random NSFW", callback_data="random")],
    [InlineKeyboardButton("⭐ My Favorites", callback_data="favorites")],
    [InlineKeyboardButton("🕓 History", callback_data="history")],
    [InlineKeyboardButton("ℹ️ About", callback_data="about")]
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 Welcome to the Ultimate NSFW Bot!\nOnly the best-rated Rule34 content.\n\nChoose an option below:",
Only the best-rated Rule34 content.

Choose an option below:",
        reply_markup=MAIN_MENU
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "search":
        await query.edit_message_text("✏️ Send me the character name to fetch top-rated NSFW images.")
    elif query.data == "random":
        await send_random_image(query.message.chat.id, context, user_id)
    elif query.data == "favorites":
        favs = user_favorites.get(user_id, [])
        if not favs:
            await query.edit_message_text("⭐ You have no favorites yet.")
        else:
            for img in favs[:5]:
                await context.bot.send_photo(chat_id=query.message.chat.id, photo=img)
    elif query.data == "history":
        hist = user_history.get(user_id, [])
        if not hist:
            await query.edit_message_text("🕓 No search history found.")
        else:
            await query.edit_message_text(f"🧠 Your recent searches:
- " + "\n- ".join(hist[-5:]))
    elif query.data == "about":
        await query.edit_message_text(
            "🤖 This bot fetches only high-rated NSFW anime images using Rule34.
"
            "Features: Favorites, History, Random and Smart Search.

"
            "Use /start to return to the menu."
        )

async def receive_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    term = update.message.text.strip()

    images = fetch_top_images(term)
    if not images:
        await update.message.reply_text("❌ No high-rated images found. Try a different name.")
        return

    user_query[user_id] = term
    user_images[user_id] = images
    user_history.setdefault(user_id, []).append(term)

    keyboard = [
        [InlineKeyboardButton("➡️ Next", callback_data="next")],
        [InlineKeyboardButton("⭐ Favorite", callback_data="fav")],
        [InlineKeyboardButton("⬅️ Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=images[0],
        caption=f"🔞 Top-rated results for: {term}",
        reply_markup=reply_markup
    )

async def next_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    term = user_query.get(user_id, "")
    images = user_images.get(user_id, [])

    if not images:
        await query.message.reply_text("⚠️ No search loaded. Send a character name first.")
        return

    image = random.choice(images)
    keyboard = [
        [InlineKeyboardButton("➡️ Next", callback_data="next")],
        [InlineKeyboardButton("⭐ Favorite", callback_data="fav")],
        [InlineKeyboardButton("⬅️ Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(chat_id=query.message.chat.id, photo=image, caption=f"🔞 {term}", reply_markup=reply_markup)

async def add_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    last_images = user_images.get(user_id, [])

    if last_images:
        img = last_images[0]
        user_favorites.setdefault(user_id, [])
        if img not in user_favorites[user_id]:
            user_favorites[user_id].append(img)
            await query.message.reply_text("⭐ Image added to favorites.")
        else:
            await query.message.reply_text("⚠️ Image already in favorites.")

async def send_random_image(chat_id, context, user_id):
    random_tags = ["asuna", "mikasa", "yor_forger", "zero_two", "tsunade"]
    term = random.choice(random_tags)
    images = fetch_top_images(term)

    if images:
        user_query[user_id] = term
        user_images[user_id] = images
        image = random.choice(images)
        await context.bot.send_photo(chat_id=chat_id, photo=image, caption=f"🎲 Random top-rated: {term}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="❌ No good images found.")

def fetch_top_images(term):
    tag = f"{term.replace(' ', '_')} rating:explicit score:>50"
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit=30&tags={tag}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return [item["file_url"] for item in data if item.get("file_url", "").endswith((".jpg", ".png", ".jpeg", ".webp"))]
    except:
        return []

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_menu))
app.add_handler(CallbackQueryHandler(next_image, pattern="^next$"))
app.add_handler(CallbackQueryHandler(add_favorite, pattern="^fav$"))
app.add_handler(CallbackQueryHandler(start, pattern="^menu$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_character))

if __name__ == "__main__":
    print("💎 Super NSFW Bot running...")
    app.run_polling()
