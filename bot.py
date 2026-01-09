import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
import google.generativeai as genai

# Logging setup - Error එකක් ආවොත් බලාගන්න
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Keys (Environment Variables හරහා ලබා ගනී)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Gemini AI Configure කිරීම (අලුත්ම gemini-1.5-flash මොඩල් එක මෙහි ඇත)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start command එක ලැබුණු විට ක්‍රියාත්මක වේ """
    welcome_text = (
        "👋 ආයුබෝවන්! මම Gemini AI මගින් ක්‍රියා කරන බොට් කෙනෙක්.\n\n"
        "ඔබට අවශ්‍ය ඕනෑම දෙයක් මගෙන් අහන්න. මම උදවු කරන්නම්!"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """පණිවිඩ ලැබෙන විට ක්‍රියාත්මක වන ප්‍රධාන කොටස"""
    user_text = update.message.text
    if not user_text:
        return

    # Bot "Typing..." ලෙස පෙන්වීමට (User ට bot වැඩ කරන බව දැනේ)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Gemini වෙතින් පිළිතුර ලබා ගැනීම
        response = model.generate_content(user_text)
        bot_reply = response.text
        
        # පිළිතුර Telegram එකට යැවීම
        await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_reply)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        # දෝෂයක් ආවොත් User ට පණිවිඩයක් යැවීම
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="සමාවන්න, මට මේ වෙලාවේ පිළිතුරක් ලබා දෙන්න බැහැ. පසුව උත්සාහ කරන්න."
        )

if __name__ == '__main__':
    # Token එක නැත්නම් Error එකක් පෙන්වීමට
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN එක ලබා දී නැත!")
    else:
        # Bot එක Build කිරීම
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # CommandHandlers සහ MessageHandlers එකතු කිරීම
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is successfully running...")
        application.run_polling()
