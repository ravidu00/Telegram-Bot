import os
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from groq import Groq

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq Client
client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot දැන් සක්‍රීයයි! මම ඉතාමත් වේගවත් Llama 3.3 භාවිතා කරනවා.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text: return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        # මෙතන තමයි වෙනස් කළේ: llama3-8b-8192 වෙනුවට llama-3.3-70b-versatile දාලා තියෙන්නේ
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile", 
        )
        reply = chat_completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Groq Error: {e}")
        # දෝෂය මොකක්ද කියලා දැනගන්න මෙහෙම දාමු
        await update.message.reply_text(f"❌ දෝෂයක්: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is starting using Llama 3.3...")
    application.run_polling(drop_pending_updates=True)
