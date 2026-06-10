import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

# Bot tokenini shu yerga yozing
TOKEN ="8236929425:AAFe9IETti_K4-9HzWX9mOBACOBljw306Qk"
# Loglarni sozlash (Xatoliklarni ko'rib turish uchun)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Botni ishga tushgandagi start komandasi
@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(
        f"Salom {message.from_user.full_name}! 👋\n\n"
        "Menga Instagram, TikTok yoki YouTube'dan video/rasm havolasini (linkini) yuboring, "
        "men uni sizga yuklab beraman!"
    )

# Link kelgandagi xendler
@dp.message(F.text.startswith("http"))
async def download_video(message: Message):
    url = message.text
    status_msg = await message.answer("⏳ Havola tekshirilmoqda va yuklanmoqda...")

    # Yuklab olinadigan fayl nomi andozasi
    outtmpl = f"downloads/{message.from_user.id}_%(title)s.%(ext)s"

    # yt-dlp sozlamalari
    ydl_opts = {
        'outtmpl': outtmpl,
        'format': 'best',  # Eng yaxshi sifatni tanlash
        'max_filesize': 50 * 1024 * 1024,  # Telegram bot uchun 50MB gacha cheklov (katta fayllar o'tmaydi)
        'quiet': True
    }

    # downloads papkasi bo'lmasa yaratish
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        # Bloklanishning oldini olish uchun yuklash jarayonini asinxron bajarish
        loop = asyncio.get_running_loop()
        
        with YoutubeDL(ydl_opts) as ydl:
            # Havola haqida ma'lumot olish va yuklash
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text("🚀 Fayl Telegram'ga yuklanmoqda...")

        # Fayl kengaytmasini tekshirish (Rasm yoki Video ekanligini bilish uchun)
        if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            photo = FSInputFile(filename)
            await message.answer_photo(photo=photo, caption="📸 Rasm yuklab olindi!")
        else:
            video = FSInputFile(filename)
            await message.answer_video(video=video, caption="🎬 Video yuklab olindi!")

        await status_msg.delete()

    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
        await status_msg.edit_text("❌ Kechirasiz, ushbu havoladan media yuklab olishning iloji bo'lmadi yoki fayl hajmi juda katta (Maksimal: 50MB).")
    
    finally:
        # Server joyini tejash uchun yuklangan faylni o'chirib tashlaymiz
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)

# Botni doimiy ishga tushirish (Polling)
async def main():
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())
