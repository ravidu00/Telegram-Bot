import os
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import google.generativeai as genai

# Logging සැකසුම්
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Gemini Configure
genai.configure(api_key=GEMINI_KEY)

# ඔයාගේ API එකට ගැලපෙන අලුත්ම සහ වේගවත්ම මාදිලිය
model = genai.GenerativeModel('gemini-2.0-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ආයුබෝවන්! මම දැන් අලුත් API එක සමඟ GitHub හරහා වැඩ කරනවා.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text: return
    
    # Bot 'Typing...' ලෙස පෙන්වීම
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        # දෝෂය කෙලින්ම chat එකේ පෙන්වයි
        await update.message.reply_text(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    # එකවර දෙපොළක Bot Run වීම (Conflict) වැළැක්වීමට drop_pending_updates භාවිතා කරයි
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is starting on GitHub Actions...")
    application.run_polling(drop_pending_updates=True)
