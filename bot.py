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

# Environment Variables වලින් API Keys ලබා ගැනීම
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Gemini AI සැකසුම් (අලුත්ම gemini-1.5-flash මොඩල් එක)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start command එක සඳහා """
    welcome_msg = "👋 ආයුබෝවන්! මම Gemini AI බොට්. ඔබට ඕනෑම දෙයක් මාගෙන් අහන්න පුළුවන්."
    await update.message.reply_text(welcome_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """පණිවිඩ ලැබෙන විට ක්‍රියාත්මක වන කොටස"""
    user_text = update.message.text
    if not user_text:
        return

    # Bot "Typing..." ලෙස පෙන්වීම
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        # Gemini AI වෙතින් පිළිතුර ලබා ගැනීම
        response = model.generate_content(user_text)
        
        # Telegram හරහා පිළිතුර යැවීම
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("සමාවන්න, පිළිතුර ලබා දීමේදී දෝෂයක් සිදු විය.")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not GEMINI_KEY:
        print("ERROR: API Keys ලබා දී නැත!")
    else:
        # Application එක සෑදීම
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Handlers සම්බන්ධ කිරීම
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is successfully running...")
        application.run_polling()
