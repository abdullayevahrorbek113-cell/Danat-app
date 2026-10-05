import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ==================== SOZLAMALAR ====================
TELEGRAM_TOKEN = "8469058145:AAHDnKQfiS-isebvX8hHwrvSo6cuoEfaNfU"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ASOSIY ADMIN (OWNER) ID VA TIZIM MA'LUMOTLARI
OWNER_ID = 8622029343
ADMIN_USERNAME = "@a_ahrorbek11"
KARTA_RAQAMI = "9860260115435265"
KARTA_EGASI = "Shamsiddinova A."

ADMINS = [OWNER_ID]
REQUIRED_CHANNELS = ["@danatapp"]

# PAYERPIN API SOZLAMALARI
PAYERPIN_API_KEY = "pp_live_xxxxxxxxxxxx"  # Payerpin-dan olingan API key
PAYERPIN_URL = "https://api.payerpin.uz/api/v2/order"

# PAYERPIN MAHSULOT ID'LARI
PAYERPIN_PRODUCT_IDS = {
    # Free Fire - Almazlar
    "110 Almaz": 101, "341 Almaz": 102, "572 Almaz": 103, "1166 Almaz": 104, "2398 Almaz": 105, "6160 Almaz": 106,
    # Free Fire - Propusklar
    "Haftalik kichkina": 107, "Evo Access 3 Kun": 108, "Haftalik obuna": 109, "Evo Access 7 Kun": 110, "Oylik Obuna": 111, "Evo Access 30 Kun": 112,
    # Free Fire - Level Up
    "6 Level Up": 113, "10 Level Up": 114, "15 Level Up": 115, "20 Level Up": 116, "25 Level Up": 117, "30 Level Up": 118,
    # PUBG Mobile
    "60 UC": 201, "120 UC": 202, "180 UC": 203, "325 UC": 204, "385 UC": 205, "660 UC": 206, "720 UC": 207, "985 UC": 208, "1320 UC": 209, "1800 UC": 210, "3850 UC": 211, "8100 UC": 212,
    # PUBG Mobile - Prime
    "1 Oy Prime": 213, "3 Oy Prime": 214, "6 Oy Prime": 215, "12 Oy Prime": 216, "1 Oy Prime Plus": 217, "3 Oy Prime Plus": 218, "6 Oy Prime Plus": 219, "12 Oy Prime Plus": 220, "Nabor pervoy pokupki": 221, "Nabor materialov": 222, "Nabor mificheskiy": 223, "Weekly Mythic Echo": 224,
    # Standoff 2
    "100 Gold": 301, "500 Gold": 302, "1000 Gold": 303, "3000 Gold": 304,
    # Mobile Legends
    "88 Olmos": 401, "257 Olmos": 402, "706 Olmos": 403, "2195 Olmos": 404
}

# NARXLAR VA BO'LIMLAR
prices = {
    "Free Fire": {
        "Almazlar": {"110 Almaz": 12000, "341 Almaz": 35000, "572 Almaz": 58000, "1166 Almaz": 115000, "2398 Almaz": 230000, "6160 Almaz": 570000},
        "Propuski": {"Haftalik kichkina": 6000, "Evo Access 3 Kun": 9000, "Haftalik obuna": 23000, "Evo Access 7 Kun": 14000, "Oylik Obuna": 80000, "Evo Access 30 Kun": 42000},
        "Level Up": {"6 Level Up": 6000, "10 Level Up": 10000, "15 Level Up": 10000, "20 Level Up": 10000, "25 Level Up": 10000, "30 Level Up": 13000}
    },
    "PUBG Mobile": {
        "AVTO 24/7 (UC)": {"60 UC": 13000, "120 UC": 26000, "180 UC": 39000, "325 UC": 65000, "385 UC": 78000, "660 UC": 125000, "720 UC": 140000, "985 UC": 190000, "1320 UC": 250000, "1800 UC": 320000, "3850 UC": 640000, "8100 UC": 1300000},
        "To'plamlar (Prime)": {"1 Oy Prime": 16000, "3 Oy Prime": 45000, "6 Oy Prime": 80000, "12 Oy Prime": 160000, "1 Oy Prime Plus": 130000, "3 Oy Prime Plus": 390000, "6 Oy Prime Plus": 750000, "12 Oy Prime Plus": 1500000, "Nabor pervoy pokupki": 22000, "Nabor materialov": 50000, "Nabor mificheskiy": 70000, "Weekly Mythic Echo": 50000}
    },
    "Standoff 2": {
        "Gold": {"100 Gold": 20000, "500 Gold": 92000, "1000 Gold": 180000, "3000 Gold": 530000}
    },
    "Mobile Legends": {
        "Olmoslar": {"88 Olmos": 25000, "257 Olmos": 70000, "706 Olmos": 185000, "2195 Olmos": 550000}
    }
}

user_data = {}
user_balances = {}
pending_amounts = {}

# ==================== PAYERPIN API FUNKSIYASI ====================
def send_payerpin_order(item_name, player_id):
    if item_name not in PAYERPIN_PRODUCT_IDS:
        return False, "Mahsulot Payerpin bazasida topilmadi."

    product_id = PAYERPIN_PRODUCT_IDS[item_name]
    headers = {"X-API-Key": PAYERPIN_API_KEY, "Content-Type": "application/json"}
    payload = {"product_id": product_id, "player_id": player_id}

    try:
        response = requests.post(PAYERPIN_URL, json=payload, headers=headers, timeout=12)
        res = response.json()
        if response.status_code == 200 and res.get("ok"):
            return True, "⚡ Donat o'yin hisobingizga muvaffaqiyatli tushirildi!"
        else:
            err_msg = res.get("error", {}).get("message", "Noma'lum API xatoligi")
            return False, f"Payerpin Xatosi: {err_msg}"
    except Exception as e:
        return False, f"Server bilan aloqa uzildi: {str(e)}"

# ==================== YORDAMCHI FUNKSIYALAR ====================
def check_subscriptions(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

def get_subscription_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📢 Kanalga obuna bo'lish", url="https://t.me/danatapp"))
    keyboard.add(InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub"))
    return keyboard

def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🎮 Donat qilish"), KeyboardButton("💰 Mening hisobim"))
    markup.add(KeyboardButton("👤 Admin bilan bog'lanish"), KeyboardButton("📋 Narxlar va qoidalar"))
    
    # Agar foydalanuvchi Admin bo'lsa, asosiy menyuga Admin Panel tugmasi ham chiqadi
    if user_id in ADMINS or user_id == OWNER_ID:
        markup.add(KeyboardButton("⚙️ Admin Panel"))
        
    return markup

def show_admin_panel(chat_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("➕ Admin Qo'shish", callback_data="admin_add"))
    keyboard.add(InlineKeyboardButton("➖ Adminni O'chirish", callback_data="admin_del"))
    keyboard.add(InlineKeyboardButton("📋 Adminlar Ro'yxati", callback_data="admin_list"))

    bot.send_message(
        chat_id, 
        "⚙️ **Admin Boshqaruv Paneli:**\n\nQuyidagi tugmalar orqali adminlarni boshqaring:", 
        reply_markup=keyboard, 
        parse_mode="Markdown"
    )

# ==================== ADMIN PANEL BUYRUQLARI ====================
@bot.message_handler(commands=['admin'])
def admin_command(message):
    user_id = message.from_user.id
    if user_id in ADMINS or user_id == OWNER_ID:
        show_admin_panel(message.chat.id)
    else:
        bot.send_message(message.chat.id, f"❌ Siz admin emassiz!\nSizning ID: `{user_id}`", parse_mode="Markdown")

def process_add_admin_id(message):
    if message.text and message.text.isdigit():
        new_id = int(message.text)
        if new_id not in ADMINS:
            ADMINS.append(new_id)
            bot.send_message(message.chat.id, f"✅ Admin muvaffaqiyatli qo'shildi: `{new_id}`", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚠️ Bu foydalanuvchi allaqachon admin!")
    else:
        bot.send_message(message.chat.id, "❌ Noto'g'ri ID kiritildi!")

def process_del_admin_id(message):
    if message.text and message.text.isdigit():
        target_id = int(message.text)
        if target_id == OWNER_ID:
            bot.send_message(message.chat.id, "❌ Asosiy adminni (Owner) o'chirib bo'lmaydi!")
            return
        if target_id in ADMINS:
            ADMINS.remove(target_id)
            bot.send_message(message.chat.id, f"✅ Admin muvaffaqiyatli o'chirildi: `{target_id}`", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚠️ ID topilmadi!")

# ==================== FOYDALANUVCHI BUYRUQLARI ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if not check_subscriptions(chat_id):
        bot.send_message(chat_id, "⚠️ **Botdan foydalanish uchun kanalga obuna bo'ling:**", reply_markup=get_subscription_keyboard(), parse_mode="Markdown")
        return

    if chat_id not in user_balances:
        user_balances[chat_id] = {"balance": 0, "history": []}

    bot.send_message(
        chat_id,
        f"Assalomu alaykum, **{message.from_user.first_name}**!\n\n"
        f"🆔 Telegram ID: `{chat_id}`\n"
        "🎮 O'yinlarga 24/7 avtomatik donat xizmati.",
        reply_markup=get_main_menu(chat_id),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['payme'])
def add_balance_manual(message):
    if message.from_user.id not in ADMINS and message.from_user.id != OWNER_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "Format: `/payme [user_id] [summa]`", parse_mode="Markdown")
        return

    target_id, amount = int(args[1]), int(args[2])
    if target_id not in user_balances:
        user_balances[target_id] = {"balance": 0, "history": []}

    user_balances[target_id]["balance"] += amount
    user_balances[target_id]["history"].append(f"• Balans to'ldirildi: +{amount:,} so'm ✅")
    bot.reply_to(message, f"✅ `{target_id}` balansiga **{amount:,} so'm** qo'shildi!", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🎮 Donat qilish", "💰 Mening hisobim", "👤 Admin bilan bog'lanish", "📋 Narxlar va qoidalar", "⚙️ Admin Panel"])
def handle_menu(message):
    chat_id = message.chat.id
    if not check_subscriptions(chat_id):
        bot.send_message(chat_id, "⚠️ **Kanalga obuna bo'ling:**", reply_markup=get_subscription_keyboard(), parse_mode="Markdown")
        return

    if chat_id not in user_balances:
        user_balances[chat_id] = {"balance": 0, "history": []}

    if message.text == "⚙️ Admin Panel":
        if chat_id in ADMINS or chat_id == OWNER_ID:
            show_admin_panel(chat_id)
        else:
            bot.send_message(chat_id, "❌ Bu bo'lim faqat adminlar uchun!")

    elif message.text == "🎮 Donat qilish":
        keyboard = InlineKeyboardMarkup()
        for g in prices.keys():
            keyboard.add(InlineKeyboardButton(f"🔥 {g}", callback_data=f"game_{g}"))
        bot.send_message(chat_id, "O'yinni tanlang:", reply_markup=keyboard)

    elif message.text == "💰 Mening hisobim":
        data = user_balances[chat_id]
        history = "\n".join(data["history"]) if data["history"] else "Tranzaksiyalar yo'q."
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("💳 Balansni to'ldirish", callback_data="topup_balance"))

        bot.send_message(
            chat_id,
            f"👤 **Shaxsiy Kabinet:**\n\n🆔 ID: `{chat_id}`\n💰 Balans: **{data['balance']:,} so'm**\n\n📜 **Tarix:**\n{history}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    elif message.text == "👤 Admin bilan bog'lanish":
        bot.send_message(chat_id, f"Admin: {ADMIN_USERNAME}")

    elif message.text == "📋 Narxlar va qoidalar":
        bot.send_message(chat_id, f"📋 **To'lov uchun karta:** `{KARTA_RAQAMI}` ({KARTA_EGASI})", parse_mode="Markdown")

# ==================== CALLBACK HANDLER ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    # Admin Callbacklar
    if call.data == "admin_add":
        if call.from_user.id in ADMINS or call.from_user.id == OWNER_ID:
            bot.send_message(chat_id, "➕ **Yangi admin ID raqamini kiriting:**", parse_mode="Markdown")
            bot.register_next_step_handler(call.message, process_add_admin_id)
        return

    elif call.data == "admin_del":
        if call.from_user.id in ADMINS or call.from_user.id == OWNER_ID:
            bot.send_message(chat_id, "➖ **O'chiriladigan admin ID raqamini kiriting:**", parse_mode="Markdown")
            bot.register_next_step_handler(call.message, process_del_admin_id)
        return

    elif call.data == "admin_list":
        if call.from_user.id in ADMINS or call.from_user.id == OWNER_ID:
            txt = "📋 **Adminlar Ro'yxati:**\n\n" + "\n".join([f"• `{a}`" for a in ADMINS])
            bot.send_message(chat_id, txt, parse_mode="Markdown")
        return

    if call.data == "check_sub":
        if check_subscriptions(chat_id):
            bot.send_message(chat_id, "✅ Obuna tasdiqlandi!", reply_markup=get_main_menu(chat_id))
        else:
            bot.answer_callback_query(call.id, "⚠️ Obuna bo'lmadingiz!", show_alert=True)
        return

    if call.data.startswith(("approve_", "reject_")):
        if call.from_user.id not in ADMINS and call.from_user.id != OWNER_ID:
            return
        act, target_id = call.data.split("_")[0], int(call.data.split("_")[1])

        if act == "approve" and target_id in pending_amounts:
            amt = pending_amounts.pop(target_id)
            user_balances[target_id]["balance"] += amt
            user_balances[target_id]["history"].append(f"• Balans: +{amt:,} so'm ✅")
            bot.edit_message_caption(f"{call.message.caption}\n\n✅ **TASDIQLANDI**", chat_id, call.message.message_id)
            bot.send_message(target_id, f"🎉 Hisobingizga **{amt:,} so'm** qo'shildi!", parse_mode="Markdown")
        else:
            pending_amounts.pop(target_id, None)
            bot.edit_message_caption(f"{call.message.caption}\n\n❌ **RAD ETILDI**", chat_id, call.message.message_id)
        return

    if call.data == "topup_balance":
        bot.send_message(chat_id, f"💳 **Karta:** `{KARTA_RAQAMI}` ({KARTA_EGASI})\n\nQancha o'tkazganingizni **faqat raqamlarda** kiriting:", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, process_topup_amount)

    elif call.data.startswith("game_"):
        g_name = call.data.split("_")[1]
        user_data[chat_id] = {"game": g_name}
        kb = InlineKeyboardMarkup()
        for cat in prices[g_name].keys():
            kb.add(InlineKeyboardButton(f"📁 {cat}", callback_data=f"cat_{g_name}_{cat}"))
        bot.edit_message_text("Bo'limni tanlang:", chat_id, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("cat_"):
        parts = call.data.split("_")
        g_name, cat_name = parts[1], parts[2]
        user_data[chat_id]["category"] = cat_name
        kb = InlineKeyboardMarkup()
        for item, pr in prices[g_name][cat_name].items():
            kb.add(InlineKeyboardButton(f"{item} — {pr:,} so'm", callback_data=f"item_{item}"))
        bot.edit_message_text("Mahsulotni tanlang:", chat_id, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("item_"):
        item_name = call.data.split("_")[1]
        user_data[chat_id]["item"] = item_name
        bot.send_message(chat_id, f"Tanlandi: **{item_name}**\n\nO'yinga tegishli **ID raqamingizni** kiriting:", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, process_player_id)

def process_topup_amount(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "⚠️️ Faqat raqam kiriting!")
        return
    user_data[message.chat.id] = {"topup_amount": int(message.text)}
    bot.send_message(message.chat.id, "Endi **to'lov chekining rasmini (skrinshot)** yuboring:")
    bot.register_next_step_handler(message, process_topup_receipt)

def process_topup_receipt(message):
    chat_id = message.chat.id
    if message.content_type == 'photo':
        amt = user_data.get(chat_id, {}).get("topup_amount", 0)
        pending_amounts[chat_id] = amt

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{chat_id}"), InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{chat_id}"))

        for adm in ADMINS:
            try:
                bot.send_photo(adm, message.photo[-1].file_id, caption=f"💳 **To'lov cheki!**\nID: `{chat_id}`\nSumma: **{amt:,} so'm**", reply_markup=kb, parse_mode="Markdown")
            except Exception:
                pass
        bot.reply_to(message, "✅ Chek adminga yuborildi. Tekshiruvdan so'ng balansingiz to'ldiriladi.")
    else:
        bot.send_message(chat_id, "⚠️ Iltimos, faqat rasm yuboring!")

def process_player_id(message):
    chat_id = message.chat.id
    player_id = message.text.strip()

    game = user_data[chat_id].get("game")
    category = user_data[chat_id].get("category")
    item = user_data[chat_id].get("item")
    price = prices[game][category][item]

    if user_balances.get(chat_id, {}).get("balance", 0) < price:
        bot.send_message(chat_id, f"❌ **Balans yetarli emas!**\nNarxi: {price:,} so'm\nBalans: {user_balances[chat_id]['balance']:,} so'm", reply_markup=get_main_menu(chat_id), parse_mode="Markdown")
        return

    bot.send_message(chat_id, "⏳ Payerpin orqali avto-donat amalga oshirilmoqda...")
    success, api_msg = send_payerpin_order(item, player_id)

    if success:
        user_balances[chat_id]["balance"] -= price
        user_balances[chat_id]["history"].append(f"• Donat: {item} (-{price:,} so'm) ✅")
        bot.send_message(chat_id, f"🎉 **Muvaffaqiyatli!**\n\n{api_msg}\n📦 Mahsulot: {item}\n🆔 O'yin ID: {player_id}", reply_markup=get_main_menu(chat_id))
    else:
        bot.send_message(chat_id, f"❌ **Donat amalga oshmadi:**\n{api_msg}", reply_markup=get_main_menu(chat_id))

print("Bot tayyor va ishlamoqda...")
bot.infinity_polling()
