import os
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import google.generativeai as genai

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Gemini AI Configure - මෙහිදී සරලව gemini-pro පාවිච්චි කරමු (වැඩිපුරම stable නිසා)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ආයුබෝවන්! දැන් මගෙන් ප්‍රශ්න අහන්න පුළුවන්.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text: return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        # AI එකෙන් පිළිතුර ලබා ගැනීම
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        # Error එක කෙලින්ම Chat එකට පෙන්වමු දෝෂය හඳුනාගන්න
        await update.message.reply_text(f"දෝෂයක්: {str(e)[:100]}")

if __name__ == '__main__':
    # Bot එක හදන කොට පරණ පණිවිඩ මඟහරින්න drop_pending_updates දාමු
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is starting...")
    # එකම Bot දෙපොළක Run වීම වැළැක්වීමට මෙය උදවු වේ
    application.run_polling(drop_pending_updates=True)
