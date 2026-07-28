import os
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# Loggingni sozlash
logging.basicConfig(level=logging.INFO)

TOKEN = "8780502309:AAFNq2PeHVkTHHBlWQjaAug1yP4malI-9WY"
CHANNEL_USERNAME = "@Pirikol_Prekol_Vidyolar"
CHANNEL_LINK = "https://t.me/Pirikol_Prekol_Vidyolar"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render port talabini qondirish uchun oddiy HTTP server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    
    def log_message(self, format, *args):
        pass  # Loglarni to'ldirib yubormasligi uchun o'chiramiz

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Obunani tekshirish
async def check_sub_channel(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logging.error(f"Obunani tekshirishda xatolik: {e}")
        return False

def get_sub_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="🔄 Tekshirish", callback_data="check_subscription")]
        ]
    )

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    if not await check_sub_channel(message.from_user.id):
        await message.answer(
            f"❌ Botdan foydalanish uchun avval kanalimizga obuna bo'ling:\n\n📢 {CHANNEL_LINK}",
            reply_markup=get_sub_keyboard()
        )
        return

    await message.answer(
        f"Assalomu alaykum! 👋\n\n"
        f"Men Instagram, Facebook, YouTube va TikTok tarmoqlaridan video yuklab beruvchi botman.\n\n"
        f"📢 Kanalimiz: {CHANNEL_LINK}\n\n🎥 Video havolasini yuboring!"
    )

@dp.callback_query(F.data == "check_subscription")
async def process_check_sub(callback: types.CallbackQuery):
    if await check_sub_channel(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer("✅ Obuna tasdiqlandi! Endi video havolasini yuborishingiz mumkin.")
    else:
        await callback.answer("❌ Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)

@dp.message(F.text.startswith("http"))
async def download_video(message: types.Message):
    if not await check_sub_channel(message.from_user.id):
        await message.answer(
            f"❌ Botdan foydalanish uchun avval kanalimizga obuna bo'ling:\n\n📢 {CHANNEL_LINK}",
            reply_markup=get_sub_keyboard()
        )
        return

    url = message.text.strip()
    processing_msg = await message.answer("⏳ Video yuklab olinmoqda, iltimos kuting...")
    output_filename = f"video_{message.from_user.id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'max_filesize': 50 * 1024 * 1024,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(output_filename):
            await message.answer_video(
                video=types.FSInputFile(output_filename),
                caption=f"✅ Marhamat!\n\n📢 Kanal: {CHANNEL_LINK}"
            )
            await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        else:
            await processing_msg.edit_text("❌ Xatolik: Video topilmadi.")
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await processing_msg.edit_text("❌ Videoni yuklab olishning iloji bo'lmadi (hajmi katta yokihavola yopiq bo'lishi mumkin).")
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Iltimos, faqat video havolasini yuboring!\n\n📢 Kanal: {CHANNEL_LINK}")

async def main():
    # HTTP serverni alohida oqimda (thread) ishga tushiramiz
    server_thread = Thread(target=run_http_server, daemon=True)
    server_thread.start()
    
    # Botni ishga tushiramiz
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
