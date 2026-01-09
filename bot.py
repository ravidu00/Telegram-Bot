import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import google.generativeai as genai

# Keys
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Gemini Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

async def moviepro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # .moviepro [ෆිල්ම් එකේ නම] ලබා ගැනීම
    movie_name = ' '.join(context.args)
    if not movie_name:
        await update.message.reply_text("❌ කරුණාකර චිත්‍රපටයේ නම ඇතුළත් කරන්න. (උදා: .moviepro Leo)")
        return

    wait_msg = await update.message.reply_text(f"🔍 {movie_name} සොයමින් පවතී...")

    try:
        # 1. Gemini ගෙන් ඒ ෆිල්ම් එක ගැන කෙටි විස්තරයක් ගැනීම
        ai_response = model.generate_content(f"Give a very short summary of the movie {movie_name} in Sinhala.")
        movie_desc = ai_response.text

        # 2. Movie Link එකක් සෙවීම (Scraping Example)
        # මෙහිදී අපි සරලව Google Search එකක් හෝ අදාළ සයිට් එකේ සර්ච් එකක් Simulate කරනවා
        search_url = f"https://www.google.com/search?q=site:sinhalasub.lk+{movie_name}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # සයිට් එකේ ලින්ක් එක සොයා ගැනීම
        links = soup.find_all('a')
        download_link = "ලින්ක් එක හමු නොවීය"
        for link in links:
            if 'sinhalasub.lk' in str(link.get('href')):
                download_link = link.get('href').split('&url=')[1].split('&')[0]
                break

        # 3. ලස්සනට පෙන්වීම
        final_msg = (
            f"🎬 *MOVIE HUB PRO*\n\n"
            f"ℹ️ *විස්තර:* {movie_desc}\n\n"
            f"📥 *Download Link:* [මෙතනින් ලබාගන්න]({download_link})\n\n"
            f"💡 _ඔබට මෙය MP4 ලෙස ලබා ගැනීමට අවශ්‍ය නම් ඉහත ලින්ක් එක Browser එකේ Open කරන්න._"
        )
        
        await wait_msg.delete()
        await update.message.reply_markdown(final_msg)

    except Exception as e:
        await update.message.reply_text(f"❌ දෝෂයක් වුණා: {str(e)}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    # .moviepro command එක Register කිරීම
    application.add_handler(CommandHandler('moviepro', moviepro))
    application.run_polling()
