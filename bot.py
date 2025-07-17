
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests
import random

# 🔑 Token do seu bot (corrigido)
TOKEN = "8044715557:AAGdxBxX1--A5efKqTsRSB71arhMD8efALk"

# Guardar o nome pesquisado por usuário
user_query = {}

# Início do bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👩‍🎤 Envie o nome da personagem de anime (ex: Asuna, Hinata, Mikasa)...")

# Recebe o nome da personagem
async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nome = update.message.text.strip()

    user_query[user_id] = nome

    teclado = [[InlineKeyboardButton("🔍 Buscar NSFW", callback_data='buscar')]]
    reply_markup = InlineKeyboardMarkup(teclado)

    await update.message.reply_text(f"Deseja buscar imagens NSFW de: *{nome}*?", reply_markup=reply_markup, parse_mode="Markdown")

# Quando o botão é clicado
async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    termo = user_query.get(user_id)

    if not termo:
        await query.edit_message_text("❗ Envie o nome da personagem antes de clicar no botão.")
        return

    await query.edit_message_text("🔎 Buscando imagens NSFW...")

    imagens = buscar_imagens_rule34(termo)

    if imagens:
        link = random.choice(imagens)
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=link)
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="Nenhuma imagem encontrada. Tente outro nome.")

# Função para buscar imagens diretamente da API JSON do Rule34
def buscar_imagens_rule34(termo):
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&limit=20&tags={termo.replace(' ', '_')}"
    try:
        r = requests.get(url, timeout=10)
        dados = r.json()
        imagens = [item["file_url"] for item in dados if item.get("file_url", "").endswith((".jpg", ".png", ".jpeg"))]
        return imagens
    except:
        return []

# Configuração do bot
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome))
app.add_handler(CallbackQueryHandler(buscar))

print("🤖 Bot rodando...")
app.run_polling()
