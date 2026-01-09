import os
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import google.generativeai as genai

# Logging සැකසුම්
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Keys ලබා ගැනීම
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Gemini AI සැකසුම්
# 404 Error එක මඟහරවා ගැනීමට මෙහි මාදිලිය නිවැරදිව ලබා දී ඇත
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start command එක """
    await update.message.reply_text("👋 ආයුබෝවන්! මම Gemini AI බොට්. ඔබට ඕනෑම දෙයක් අහන්න පුළුවන්.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """පණිවිඩ හැසිරවීම"""
    user_text = update.message.text
    if not user_text:
        return

    # Typing action එක පෙන්වීම
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        # Gemini AI වෙතින් පිළිතුර ලබා ගැනීම
        response = model.generate_content(user_text)
        
        # පිළිතුර යැවීම
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        # දෝෂය පෙන්වීම (පරීක්ෂා කිරීම සඳහා)
        await update.message.reply_text(f"දෝෂයක් සිදු විය: {str(e)[:100]}")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN එක නැත!")
    else:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is running...")
        application.run_polling()
