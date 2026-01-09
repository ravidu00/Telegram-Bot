import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# Logging setup (වැරදි සොයා ගැනීමට)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Keys ලබා ගැනීම (Environment Variables වලින්)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Gemini AI Configure කිරීම
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """පණිවිඩ ලැබෙන විට ක්‍රියාත්මක වන කොටස"""
    user_text = update.message.text
    
    if not user_text:
        return

    # Bot "Typing..." ලෙස පෙන්වීමට
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Gemini හරහා පිළිතුර ලබා ගැනීම
        response = model.generate_content(user_text)
        bot_reply = response.text
        
        # පිළිතුර යැවීම
        await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_reply)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="සමාවන්න, මට පිළිතුරක් ලබා දීමට නොහැකි වුණා. කරුණාකර නැවත උත්සාහ කරන්න."
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start විධානය ලැබුණු විට """
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="ආයුබෝවන්! මම Gemini AI මගින් ක්‍රියා කරන බොට් කෙනෙක්. ඔබට ඕනෑම දෙයක් මාගෙන් අහන්න පුළුවන්."
    )

if __name__ == '__main__':
    # Bot එක Build කිරීම
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Handlers එකතු කිරීම
    from telegram.ext import CommandHandler
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running...")
    application.run_polling()
