import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import yt_dlp

# Loggingni sozlash
logging.basicConfig(level=logging.INFO)

# Tokeningiz va kanalingiz
TOKEN = "8780502309:AAFNq2PeHVkTHHBlWQjaAug1yP4malI-9WY"
CHANNEL_LINK = "https://t.me/Pirikol_Prekol_Vidyolar"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Start komandasi
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        f"Assalomu alaykum! 👋\n\n"
        f"Men **Instagram, Facebook, YouTube va TikTok** tarmoqlaridan video yuklab beruvchi botman.\n\n"
        f"📢 Bizning kanalimiz: {CHANNEL_LINK}\n\n"
        "🎥 Menga yuklab olmoqchi bo'lgan **video havolasini (linkini)** yuboring!"
    )

# Havolalarni qabul qilish va yuklab olish
@dp.message(F.text.startswith("http"))
async def download_video(message: types.Message):
    url = message.text.strip()
    
    processing_msg = await message.answer("⏳ Video yuklab olinmoqda, iltimos kuting...")
    
    output_filename = f"video_{message.from_user.id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'max_filesize': 50 * 1024 * 1024, # 50 MB cheklov
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(output_filename):
            video_file = types.FSInputFile(output_filename)
            await message.answer_video(
                video=video_file,
                caption=f"✅ Marhamat, videongiz tayyor!\n\n📢 Kanalimiz: {CHANNEL_LINK}\n🤖 Bot: @danatchiappbot"
            )
            await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        else:
            await processing_msg.edit_text("❌ Xatolik: Video fayli topilmadi.")

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await processing_msg.edit_text(
            "❌ Videoni yuklab olishning iloji bo'lmadi.\n"
            "Sabablari:\n"
            "• Havola noto'g'ri bo'lishi mumkin.\n"
            "• Video yoki sahifa yopiq bo'lishi mumkin.\n"
            "• Video hajmi 50 MB dan katta bo'lishi mumkin."
        )
    
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Iltimos, faqat video havolasini yuboring!\n\n📢 Kanal: {CHANNEL_LINK}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
