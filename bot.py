import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# Loggingni sozlash
logging.basicConfig(level=logging.INFO)

# Tokeningiz va kanal ma'lumotlari
TOKEN = "8780502309:AAFNq2PeHVkTHHBlWQjaAug1yP4malI-9WY"
CHANNEL_USERNAME = "@Pirikol_Prekol_Vidyolar"
CHANNEL_LINK = "https://t.me/Pirikol_Prekol_Vidyolar"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Kanallarga obuna bo'lganligini tekshirish funksiyasi
async def check_sub_channel(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        # Agar foydalanuvchi tark etmagan, bloklamagan bo'lsa (creator, administrator, member)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logging.error(f"Obunani tekshirishda xatolik: {e}")
        return False

# Obunani tekshirish uchun tugma
def get_sub_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="🔄 Tekshirish", callback_data="check_subscription")]
        ]
    )
    return keyboard

# Start komandasi
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    is_subscribed = await check_sub_channel(user_id)
    
    if not is_subscribed:
        await message.answer(
            f"❌ Botdan foydalanish uchun avval quyidagi kanalimizga obuna bo'lishingiz kerak:\n\n"
            f"📢 {CHANNEL_LINK}\n\n"
            "Obuna bo'lgach, **🔄 Tekshirish** tugmasini bosing!",
            reply_markup=get_sub_keyboard()
        )
        return

    await message.answer(
        f"Assalomu alaykum! 👋\n\n"
        f"Men **Instagram, Facebook, YouTube va TikTok** tarmoqlaridan video yuklab beruvchi botman[span_1](start_span)[span_1](end_span).\n\n"
        f"📢 Bizning kanalimiz: {CHANNEL_LINK}\n\n"
        "🎥 Menga yuklab olmoqchi bo'lgan **video havolasini (linkini)** yuboring!"
    )

# Tekshirish tugmasi bosilganda
@dp.callback_query(F.data == "check_subscription")
async def process_check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed = await check_sub_channel(user_id)
    
    if is_subscribed:
        await callback.message.delete()
        await callback.message.answer(
            "✅ Rahmat! Obuna tasdiqlandi.\n\n"
            "🎥 Endi menga yuklab olmoqchi bo'lgan **video havolasini (linkini)** yuboring!"
        )
    else:
        await callback.answer("❌ Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)

# Havolalarni qabul qilish va yuklab olish
@dp.message(F.text.startswith("http"))
async def download_video(message: types.Message):
    user_id = message.from_user.id
    is_subscribed = await check_sub_channel(user_id)
    
    if not is_subscribed:
        await message.answer(
            f"❌ Botdan foydalanish uchun avval kanalimizga obuna bo'lishingiz kerak:\n\n"
            f"📢 {CHANNEL_LINK}",
            reply_markup=get_sub_keyboard()
        )
        return

    url = message.text.strip()
    processing_msg = await message.answer("⏳ Video yuklab olinmoqda, iltimos kuting...")
    output_filename = f"video_{message.from_user.id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'max_filesize': 50 * 1024 * 1024, # 50 MB cheklov[span_2](start_span)[span_2](end_span)
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(output_filename):
            video_file = types.FSInputFile(output_filename)
            await message.answer_video(
                video=video_file,
                caption=f"✅ Marhamat, videongiz tayyor!\n\n📢 Kanalimiz: {CHANNEL_LINK}\n🤖 Bot: @danatchiappbot[span_3](start_span)"[span_3](end_span)
            )
            await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        else:
            await processing_msg.edit_text("❌ Xatolik: Video fayli topilmadi.")[span_4](start_span)[span_4](end_span)

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await processing_msg.edit_text(
            "❌ Videoni yuklab olishning iloji bo'lmadi.\n"
            "Sabablari:\n"
            "• Havola noto'g'ri bo'lishi mumkin.\n"
            "• Video yoki sahifa yopiq (shaxsiy) bo'lishi mumkin.\n"
            "• Video hajmi 50 MB dan katta bo'lishi mumkin.[span_5](start_span)"[span_5](end_span)
        )
    
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Iltimos, faqat video havolasini yuboring!\n\n📢 Kanal: {CHANNEL_LINK}")[span_6](start_span)[span_6](end_span)

# Render bepul "Web Service" talabini bajarish uchun soxta veb-server (Dummy Web Server)
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    # Veb-server va bot polingini birgalikda ishga tushiramiz
    await web_server()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
