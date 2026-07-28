import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@Pirikol_Prekol_Vidyolar"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def check_sub_channel(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    return False

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    is_subscribed = await check_sub_channel(user_id)
    
    if not is_subscribed:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📢 Kanalga obuna bo'lish", url="https://t.me/Pirikol_Prekol_Vidyolar"),
            InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription")
        )
        await message.answer(
            "Botdan foydalanish uchun avval quyidagi kanalimizga obuna bo'ling va keyin 'Tekshirish' tugmasini bosing:",
            reply_markup=markup
        )
    else:
        await message.answer("Assalomu alaykum! Menga Instagram, YouTube, TikTok yoki Facebook'dan video havolasini yuboring, men uni sizga yuklab beraman!")

@dp.callback_query_handler(lambda c: c.data == 'check_subscription')
async def process_check_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    is_subscribed = await check_sub_channel(user_id)
    
    if is_subscribed:
        await bot.answer_callback_query(callback_query.id, text="Rahmat, obuna tasdiqlandi!")
        await bot.send_message(
            user_id, 
            "Obunangiz tasdiqlandi! Endi istalgan ijtimoiy tarmoq havolasini yuborishingiz mumkin."
        )
        try:
            await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        except Exception:
            pass
    else:
        await bot.answer_callback_query(callback_query.id, text="Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)

@dp.message_handler()
async def download_video(message: types.Message):
    user_id = message.from_user.id
    is_subscribed = await check_sub_channel(user_id)
    
    if not is_subscribed:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📢 Kanalga obuna bo'lish", url="https://t.me/Pirikol_Prekol_Vidyolar"),
            InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription")
        )
        await message.answer("Iltimos, avval kanalimizga obuna bo'ling:", reply_markup=markup)
        return

    url = message.text
    if "http" in url:
        await message.answer("⏳ Video yuklab olinmoqda, biroz kuting...")
    else:
        await message.answer("Iltimos, to'g'ri havola yuboring.")

# Render uchun zudlik bilan port ochuvchi HTTP server
async def handle(request):
    return web.Response(text="Bot is running and active!")

app = web.Application()
app.router.add_get('/', handle)

async def on_startup(app):
    # Bot pollingni alohida task sifatida ishga tushiramiz
    asyncio.create_task(executor.start_polling(dp, skip_updates=True))

if __name__ == '__main__':
    import asyncio
    # Render beradigan portni olamiz
    port = int(os.environ.get("PORT", 10000))
    app.on_startup.append(on_startup)
    web.run_app(app, host='0.0.0.0', port=port)
