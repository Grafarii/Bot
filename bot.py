
import random
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Token diretamente inserido no código (NÃO recomendado em produção pública)
TOKEN = "8044715557:AAGdxBxX1--A5efKqTsRSB71arhMD8efALk"

user_query = {}
user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔞 Envie o nome de uma personagem de anime para buscar imagens NSFW do Rule34.")

async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    termo = update.message.text.strip()

    imagens = buscar_imagens_rule34(termo)
    if not imagens:
        await update.message.reply_text("❌ Nenhuma imagem encontrada. Tente outro nome.")
        return

    user_query[user_id] = termo
    user_images[user_id] = imagens

    teclado = [[InlineKeyboardButton("➡️ Próxima imagem", callback_data="proxima")]]
    reply_markup = InlineKeyboardMarkup(teclado)

    await update.message.reply_photo(photo=imagens[0], caption=f"🔞 Resultados para: {termo}", reply_markup=reply_markup)

async def proxima_imagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    imagens = user_images.get(user_id, [])
    if imagens:
        imagem = random.choice(imagens)
        teclado = [[InlineKeyboardButton("➡️ Próxima imagem", callback_data="proxima")]]
        reply_markup = InlineKeyboardMarkup(teclado)
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=imagem, reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="⚠️ Nenhuma imagem salva. Envie o nome de uma personagem primeiro.")

def buscar_imagens_rule34(termo):
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit=20&tags={termo.replace(' ', '_')}"
    try:
        r = requests.get(url, timeout=10)
        dados = r.json()
        imagens = [item["file_url"] for item in dados if item.get("file_url", "").endswith((".jpg", ".png", ".jpeg", ".webp"))]
        return imagens
    except:
        return []

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome))
app.add_handler(CallbackQueryHandler(proxima_imagem))

if __name__ == "__main__":
    print("🤖 Bot rodando...")
    app.run_polling()
