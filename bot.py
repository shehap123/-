import os
import logging
import yt_dlp
import nest_asyncio  # إضافة مكتبة nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# تفعيل nest_asyncio
nest_asyncio.apply()

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# إنشاء مجلد downloads إذا لم يكن موجودًا
if not os.path.exists('downloads'):
    os.makedirs('downloads')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('مرحبًا! أرسل لي رابط فيديو أو صورة لتنزيله.')

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text('جاري تنزيل الملف...')

    try:
        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # تخزين مؤقت في مجلد
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',  # تحويل الفيديو إذا لزم الأمر
                'preferedformat': 'mp4',  # نوع الفيديو المفضل
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', None)
            filename = f"downloads/{title}.{info['ext']}"  # المسار الكامل

        # إرسال الفيديو إلى الدردشة
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video_file)

    except Exception as e:
        await update.message.reply_text(f'حدث خطأ: {str(e)}')

async def main():
    app = ApplicationBuilder().token("YOUR_TOKEN").build()  # استبدل YOUR_TOKEN بالتوكن الخاص بك
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    await app.run_polling()

# استخدم asyncio.run لتشغيل البرنامج
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
