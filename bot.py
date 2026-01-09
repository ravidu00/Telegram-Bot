import os
import logging
from telegram import Update, ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import google.generativeai as genai

# Logging සැකසුම් (Error හඳුනා ගැනීමට)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment Variables වලින් API Keys ලබා ගැනීම
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Gemini AI සැකසුම්
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# /start command එක සඳහා
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_msg = (
        f"👋 ආයුබෝවන් {user_name}!\n\n"
        "මම Gemini AI මගින් ක්‍රියා කරන Movie Helper Bot කෙනෙක්.\n\n"
        "🌟 **ඔබට කළ හැකි දේ:**\n"
        "- ඕනෑම වසරක නමක් ලබා දී එම වසරේ චිත්‍රපට ලැයිස්තුවක් ඉල්ලන්න.\n"
        "- ඕනෑම විෂයයක් ගැන මගෙන් ප්‍රශ්න අසන්න.\n\n"
        "උදාහරණ: '2024 වසරේ හොඳම movies මොනවාද?'"
    )
    await update.message.reply_text(welcome_msg)

# /help command එක සඳහා
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "ඔබට අවශ්‍ය ඕනෑම ප්‍රශ්නයක් කෙලින්ම Type කර එවන්න. මම ඒ සඳහා පිළිතුරු ලබා දෙන්නම්."
    await update.message.reply_text(help_text)

# සාමාන්‍ය පණිවිඩ සහ Movie ප්‍රශ්න හැසිරවීම
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    # Bot "Typing..." ලෙස පෙන්වීම
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Gemini AI වෙතින් පිළිතුර ලබා ගැනීම
        # මෙහිදී අපිට AI එකට movie list එකක් විදිහට එවන්න කියලා විශේෂයෙන් කියන්න පුළුවන්
        prompt = f"පහත ප්‍රශ්නයට පිළිතුරු දෙන්න. එය movie එකක් ගැන නම් ලස්සන ලැයිස්තුවක් ලෙස දෙන්න: {user_text}"
        response = model.generate_content(prompt)
        
        # Telegram හරහා පිළිතුර යැවීම
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("සමාවන්න, දෝෂයක් සිදු විය. කරුණාකර ඔබගේ API Keys පරීක්ෂා කරන්න.")

if __name__ == '__main__':
    # Token එක පරීක්ෂා කිරීම
    if not TELEGRAM_TOKEN or not GEMINI_KEY:
        print("ERROR: API Keys ලබා දී නැත! කරුණාකර Environment Variables පරීක්ෂා කරන්න.")
    else:
        # Application එක සෑදීම
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # විධානයන් (Commands) සම්බන්ධ කිරීම
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('help', help_command))
        
        # සාමාන්‍ය පණිවිඩ (Text Messages) සම්බන්ධ කිරීම
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Bot is active and running...")
        application.run_polling()
