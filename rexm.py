import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "SIZNING_BOT_TOKENINGIZ"
WEBAPP_URL = "SIZNING_WEBAPP_HOSTING_URL_MANZILINGIZ" # Masalan: https://sitingiz.uz

bot = Bot(token=TOKEN)
dp = Dispatcher()

# /start buyrug'i - Do'konga kirish tugmasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Do'konni ochish (Web App)", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer(
        "Salom! Xush kelibsiz. O'yin valyutalari va Telegram Stars'ni avtomatik xarid qilish uchun pastdagi tugmani bosing:",
        reply_markup=kb
    )

# Web App'dan kelgan ma'lumotlarni qabul qilish va avtomatik qayta ishlash
@dp.message(F.web_app_data)
async def web_app_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        product = data.get("product")
        price = data.get("price")
        
        user_id = message.from_user.id
        
        # Bu yerda avtomatik yetkazib berish logikasi bajariladi:
        # 1. Foydalanuvchi balansidan pul yechish yoki to'lov statusini tekshirish
        # 2. Novapin yoki boshqa API orqali o'yin ID raqamiga UC/Diamond yuborish
        
        await message.answer(
            f"✅ Buyurtmangiz qabul qilindi!\n\n"
            f"📦 Mahsulot: <b>{product}</b>\n"
            f"💰 Narxi: <b>{price} so'm</b>\n\n"
            f"🔄 Avtomatik tarzda hisobingizga o'tkazilmoqda..."
        )
        
        # Simulyatsiya (Avtomatik yetkazib berildi deb xabar berish)
        await asyncio.sleep(2)
        await message.answer(f"🎉 Tabriklaymiz! <b>{product}</b> muvaffaqiyatli yetkazib berildi.")
        
    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Danat bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
