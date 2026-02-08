import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yt_dlp

# Yahan apna Bot Token daliye jo BotFather se mila hai
BOT_TOKEN = "8596115520:AAFFmIIk_SNPT0bGu7EUL4nXy3eBAHhhQJc"

# Logging setup (Debugging ke liye)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Mujhe koi bhi video link (YouTube, Insta, Snapchat, etc.) bhejo, main download karke dunga."
    )

# Video download aur send karne ka logic
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # User ko batayein ki process shuru ho gaya hai
    status_msg = await update.message.reply_text("⏳ Video download ho raha hai, please wait...")

    try:
        # yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Best quality MP4
            'outtmpl': 'downloads/%(title)s.%(ext)s', # Save location
            'quiet': True,
            'max_filesize': 50 * 1024 * 1024  # 50MB limit (Telegram Bot API limit)
        }

        filename = None
        
        # Video Download karna
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Telegram par upload karna
        await update.message.reply_text("📤 Uploading...")
        
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption=info.get('title', 'Video'))

        # Cleanup: Downloaded file ko delete karna space bachane ke liye
        if os.path.exists(filename):
            os.remove(filename)
            
        await status_msg.delete() # Status msg delete karein

    except Exception as e:
        error_text = str(e)
        if "File is larger than" in error_text:
            await update.message.reply_text("❌ Ye video 50MB se badi hai, Telegram bot API ise send nahi kar sakta.")
        else:
            await update.message.reply_text(f"❌ Error aaya: Link check karein ya shayad account private hai.")
            print(e)

if __name__ == '__main__':
    # Bot Application create karein
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers add karein
    start_handler = CommandHandler('start', start)
    # Ye handler text messages (links) ko pakdega
    video_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), download_video)

    application.add_handler(start_handler)
    application.add_handler(video_handler)

    print("Bot start ho gaya hai...")
    application.run_polling()