import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import requests
import secrets
import threading
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import uvicorn

# ==================== BOT VA SOZLAMALAR ====================
TOKEN = "8469058145:AAH9pQvWiyyYmopL5nnqD_9XVjnU0T6_WRE"
bot = telebot.TeleBot(TOKEN)

SERVER_DOMAIN = "http://YOUR_SERVER_IP:8000"

ADMINS = [8622029343]  
ADMIN_USERNAME = "@a_ahrorbek11"
KARTA_RAQAMI = "9860260115435265"
KARTA_EGASI = "Shamsiddinova A."

REQUIRED_CHANNELS = ["@danatapp"]

# Foiz emas, har bir xarid uchun beriladigan aniq PUL miqdori (so'mda)
REFERRAL_BONUS_SUM = 2000 

PAYERPIN_API_KEY = "pp_live_6ADwQ1lCogyY-QeD7_xx2knKO6YQ8sAE"
PAYERPIN_URL = "https://api.payerpin.uz/api/v2/order"

PAYERPIN_PRODUCT_IDS = {
    "110 Almaz": 101, "341 Almaz": 102, "572 Almaz": 103,
    "60 UC": 201, "325 UC": 204, "660 UC": 206
}

prices = {
    "⭐ Telegram Stars": {
        "Stars Paketlari": {
            "50 Stars": 15000, "100 Stars": 29000, "250 Stars": 70000,
            "500 Stars": 138000, "1000 Stars": 270000
        },
        "Obunalar": {
            "Telegram Premium 3 Oy": 140000, "Telegram Premium 6 Oy": 210000, "Telegram Premium 12 Oy": 380000
        }
    },
    "🔥 Free Fire": {
        "Almazlar": {
            "110 Almaz": 12000, "341 Almaz": 35000, "572 Almaz": 58000,
            "1166 Almaz": 115000, "2398 Almaz": 230000, "6160 Almaz": 570000
        },
        "Propuski": {
            "Haftalik kichkina": 6000, "Evo Access 3 Kun": 9000, "Haftalik obuna": 23000,
            "Evo Access 7 Kun": 14000, "Oylik Obuna": 80000, "Evo Access 30 Kun": 42000
        },
        "Level Up": {
            "6 Level Up": 6000, "10 Level Up": 10000, "15 Level Up": 10000,
            "20 Level Up": 10000, "25 Level Up": 10000, "30 Level Up": 13000
        }
    },
    "🎯 PUBG Mobile": {
        "AVTO 24/7 (UC)": {
            "60 UC": 13000, "120 UC": 26000, "180 UC": 39000, "325 UC": 65000,
            "385 UC": 78000, "660 UC": 125000, "720 UC": 140000, "985 UC": 190000,
            "1320 UC": 250000, "1800 UC": 320000, "3850 UC": 640000, "8100 UC": 1300000
        },
        "To'plamlar (Prime)": {
            "1 Oy Prime": 16000, "3 Oy Prime": 45000, "6 Oy Prime": 80000, "12 Oy Prime": 160000,
            "1 Oy Prime Plus": 130000, "3 Oy Prime Plus": 390000, "6 Oy Prime Plus": 750000,
            "12 Oy Prime Plus": 1500000, "Nabor pervoy pokupki": 22000, "Nabor materialov": 50000,
            "Nabor mificheskiy": 70000, "Weekly Mythic Echo": 50000
        }
    },
    "🔫 Standoff 2": {
        "Gold": {
            "100 Gold": 20000, "500 Gold": 92000, "1000 Gold": 180000, "3000 Gold": 530000
        }
    },
    "🛡 Mobile Legends": {
        "Olmoslar": {
            "88 Olmos": 25000, "257 Olmos": 70000, "706 Olmos": 185000, "2195 Olmos": 550000
        }
    }
}

user_data = {}
user_balances = {}
pending_amounts = {}
referrers = {}
referral_earnings = {}
user_api_keys = {}
api_keys_db = {}
promo_codes = {}  # Promokodlar bazasi: {"CODE": {"amount": 5000, "uses": 10, "used_by": []}}

# ==================== FASTAPI SERVER (API FIX) ====================
app = FastAPI(title="Bot API Provider")

class OrderRequest(BaseModel):
    product_name: str
    player_id: str

class StarsOrderRequest(BaseModel):
    stars_amount: int
    telegram_id: int

def verify_api_key(x_api_key: str = Header(None, alias="X-API-KEY")):
    if not x_api_key or x_api_key not in api_keys_db:
        raise HTTPException(status_code=401, detail="Noto'g'ri yoki kalit kiritilmagan!")
    return api_keys_db[x_api_key]

@app.post("/v1/order")
def api_create_order(order: OrderRequest, partner_id: int = Depends(verify_api_key)):
    found_price = None
    for game in prices.values():
        for cat in game.values():
            if order.product_name in cat:
                found_price = cat[order.product_name]
                break
    
    if not found_price:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi!")

    partner_bal = user_balances.get(partner_id, {}).get("balance", 0)
    if partner_bal < found_price:
        raise HTTPException(status_code=400, detail="Mablag' yetarli emas!")

    user_balances[partner_id]["balance"] -= found_price
    user_balances[partner_id]["history"].append(f"• API Order: {order.product_name} (-{found_price:,} so'm)")
    
    success, msg = send_payerpin_order(order.product_name, order.player_id)
    if success:
        return {"status": "success", "message": "Buyurtma berildi", "remained_balance": user_balances[partner_id]["balance"]}
    else:
        user_balances[partner_id]["balance"] += found_price
        raise HTTPException(status_code=500, detail=f"Xato: {msg}")

@app.post("/v1/stars")
def api_create_stars_order(order: StarsOrderRequest, partner_id: int = Depends(verify_api_key)):
    star_rate = 280
    total_price = order.stars_amount * star_rate

    partner_bal = user_balances.get(partner_id, {}).get("balance", 0)
    if partner_bal < total_price:
        raise HTTPException(status_code=400, detail="Mablag' yetarli emas!")

    user_balances[partner_id]["balance"] -= total_price
    user_balances[partner_id]["history"].append(f"• API Stars: {order.stars_amount} ⭐ (-{total_price:,} so'm)")
    
    for adm in ADMINS:
        try: bot.send_message(adm, f"⭐ **API Stars Buyurtma!**\nHamkor: `{partner_id}`\nID: `{order.telegram_id}`\nMiqdor: **{order.stars_amount} Stars**", parse_mode="Markdown")
        except: pass

    return {"status": "success", "message": "Stars yuborildi!", "remained_balance": user_balances[partner_id]["balance"]}

# ==================== YORDAMCHI FUNKSIYALAR ====================
def check_subscriptions(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']: return False
        except Exception as e:
            print(e)
            return False
    return True

def send_payerpin_order(product_name, player_id):
    product_id = PAYERPIN_PRODUCT_IDS.get(product_name)
    if not product_id: return False, "Avto-sozlanmagan."
    headers = {"Authorization": f"Bearer {PAYERPIN_API_KEY}", "Content-Type": "application/json"}
    payload = {"product_id": product_id, "account_id": player_id}
    try:
        res = requests.post(PAYERPIN_URL, json=payload, headers=headers, timeout=10).json()
        if res.get("status") in [True, "success", 1]: return True, "Muvaffaqiyatli"
        return False, res.get("message", "Xato")
    except Exception as e:
        return False, str(e)

# ==================== KEYBOARDS ====================
def get_subscription_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 Kanalga obuna bo'lish", url="https://t.me/danatapp"))
    kb.add(InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub"))
    return kb

def get_main_menu(user_id=None):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🎮 Donat qilish"), KeyboardButton("💰 Mening hisobim"))
    markup.add(KeyboardButton("🎁 Promokod"), KeyboardButton("🔗 Taklif havolasi"))
    markup.add(KeyboardButton("👥 Taklif qilinganlar"), KeyboardButton("🔌 API Hamkorlik"))
    markup.add(KeyboardButton("👤 Admin bilan bog'lanish"), KeyboardButton("📋 Narxlar va qoidalar"))
    if user_id in ADMINS:
        markup.add(KeyboardButton("⚙️ Admin Panel"))
    return markup

def get_api_text_and_kb(chat_id):
    if chat_id not in user_api_keys:
        new_key = "key_" + secrets.token_hex(16)
        user_api_keys[chat_id] = new_key
        api_keys_db[new_key] = chat_id
    
    user_key = user_api_keys[chat_id]
    bal = user_balances.get(chat_id, {}).get("balance", 0)

    api_text = (
        "⚙️ **Xizmatlaringizni avtomatlashtiring va o'z platformangizga ulang.**\n\n"
        "🎮 **Donat / O'yinlar API:**\n"
        f"`{SERVER_DOMAIN}/v1/order`\n\n"
        "⭐ **Telegram Stars API:**\n"
        f"`{SERVER_DOMAIN}/v1/stars`\n\n"
        "🔑 **Sizning kalitingiz (X-API-KEY):**\n"
        f"`{user_key}`\n\n"
        f"💰 **Balans:** {bal:,} so'm\n"
        "⚠️ **API kalitni xech kimga bermang!**"
    )

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📄 Donat API Docs", url=f"{SERVER_DOMAIN}/docs"),
        InlineKeyboardButton("⭐ Stars API Docs", url=f"{SERVER_DOMAIN}/docs")
    )
    kb.add(InlineKeyboardButton("🔄 API kalitni yangilash", callback_data="renew_api_key"))
    kb.add(InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_main"))
    return api_text, kb

# ==================== BOT HANDLERS ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    args = message.text.split()
    
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != chat_id and chat_id not in referrers and chat_id not in user_balances:
            referrers[chat_id] = ref_id
            try: bot.send_message(ref_id, f"🎉 **Sizning havolangiz orqali yangi do'stingiz kirdi!**")
            except: pass

    if not check_subscriptions(chat_id):
        bot.send_message(chat_id, "⚠️ **Botdan foydalanish uchun kanallarimizga obuna bo'ling:**", reply_markup=get_subscription_keyboard(), parse_mode="Markdown")
        return

    if chat_id not in user_balances:
        user_balances[chat_id] = {"balance": 0, "history": []}
        
    bot.send_message(
        chat_id,
        f"Assalomu alaykum, **{message.from_user.first_name}**!\n\n"
        f"🆔 Telegram ID: `{chat_id}`\n\n"
        "🎮 O'yinlar va Telegram Stars bo'limiga xush kelibsiz!",
        reply_markup=get_main_menu(chat_id),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.text in [
    "🎮 Donat qilish", "💰 Mening hisobim", "🎁 Promokod", "🔗 Taklif havolasi", 
    "👥 Taklif qilinganlar", "🔌 API Hamkorlik", "👤 Admin bilan bog'lanish", 
    "📋 Narxlar va qoidalar", "⚙️ Admin Panel"
])
def handle_menu(message):
    chat_id = message.chat.id
    
    if not check_subscriptions(chat_id):
        bot.send_message(chat_id, "⚠️ **Avval kanallarga obuna bo'ling:**", reply_markup=get_subscription_keyboard(), parse_mode="Markdown")
        return

    if chat_id not in user_balances:
        user_balances[chat_id] = {"balance": 0, "history": []}

    if message.text == "🎮 Donat qilish":
        keyboard = InlineKeyboardMarkup(row_width=2)
        for idx, game_title in enumerate(prices.keys()):
            keyboard.add(InlineKeyboardButton(f"{game_title}", callback_data=f"game_{idx}"))
        bot.send_message(chat_id, "🎮 **Kerakli o'yin yoki xizmatni tanlang:**", reply_markup=keyboard, parse_mode="Markdown")
        
    elif message.text == "💰 Mening hisobim":
        data = user_balances[chat_id]
        history_text = "\n".join(data["history"]) if data["history"] else "Hozircha tranzaksiyalar tarixi bo'sh."
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("💳 Balansni to'ldirish", callback_data="topup_balance"))
        
        text = (
            f"👤 **Foydalanuvchi kabineti:**\n\n"
            f"🆔 Telegram ID: `{chat_id}`\n"
            f"💰 Balans: **{data['balance']:,} so'm**\n\n"
            f"📜 **Tarix:**\n{history_text}"
        )
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")

    elif message.text == "🎁 Promokod":
        msg = bot.send_message(chat_id, "🎟 **Promokodni kiriting:**", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_use_promo)

    elif message.text == "🔗 Taklif havolasi":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={chat_id}"
        share_text = f"🎮 O'yinlarga tezkor va arzon donat qilish uchun botimizga kiring!\n👉 {ref_link}"
        
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📤 Do'stlarga ulashish", switch_inline_query=share_text))

        text = (
            f"🔗 **Sizning taklif havolangiz:**\n\n"
            f"`{ref_link}`\n\n"
            f"🎁 Do'stingiz xaridi uchun **{REFERRAL_BONUS_SUM:,} so'm pul** balansingizga o'tadi!"
        )
        bot.send_message(chat_id, text, reply_markup=kb, parse_mode="Markdown")

    elif message.text == "👥 Taklif qilinganlar":
        invited_count = list(referrers.values()).count(chat_id)
        earned = referral_earnings.get(chat_id, 0)
        text = (
            f"👥 **Takliflaringiz statistikasi:**\n\n"
            f"• Taklif qilinganlar: **{invited_count} ta**\n"
            f"• Ishlab topilgan pul: **{earned:,} so'm**"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown")

    elif message.text == "🔌 API Hamkorlik":
        api_text, kb = get_api_text_and_kb(chat_id)
        bot.send_message(chat_id, api_text, reply_markup=kb, parse_mode="Markdown")

    elif message.text == "👤 Admin bilan bog'lanish":
        bot.send_message(chat_id, f"Murojaat uchun admin: {ADMIN_USERNAME}")

    elif message.text == "📋 Narxlar va qoidalar":
        rules_text = (
            "📋 **Qoidalar va Ish tartibi:**\n\n"
            "1. Kerakli xizmat va mahsulotni tanlang.\n"
            "2. O'yin yoki Telegram ID raqamingizni kiriting.\n"
            "3. Pul avtomatik hisobingizdan yechiladi.\n\n"
            f"💳 Karta: `{KARTA_RAQAMI}` ({KARTA_EGASI})"
        )
        bot.send_message(chat_id, rules_text, parse_mode="Markdown")

    elif message.text == "⚙️ Admin Panel" and chat_id in ADMINS:
        show_admin_panel(chat_id)

# ==================== ADMIN PANEL ====================
def show_admin_panel(admin_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🏷 Narxlarni O'zgartirish", callback_data="admin_edit_price"))
    kb.add(InlineKeyboardButton("🎟 Promokod Yaratish", callback_data="admin_create_promo"))
    kb.add(InlineKeyboardButton("➕ Admin Qo'shish / O'chirish", callback_data="admin_manage_admins"))
    kb.add(InlineKeyboardButton("💰 Referral Pul Bonusini O'zgartirish", callback_data="admin_set_ref"))
    bot.send_message(admin_id, "⚙️ **Admin Boshqaruv Paneli**", parse_mode="Markdown", reply_markup=kb)

# ==================== CALLBACKS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    if call.data == "check_sub":
        if check_subscriptions(chat_id):
            try: bot.delete_message(chat_id, call.message.message_id)
            except: pass
            bot.send_message(chat_id, "✅ Obunangiz tasdiqlandi!", reply_markup=get_main_menu(chat_id))
        else:
            bot.answer_callback_query(call.id, "⚠️ Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)
        return

    elif call.data == "renew_api_key":
        if chat_id in user_api_keys:
            old_key = user_api_keys[chat_id]
            if old_key in api_keys_db: del api_keys_db[old_key]

        new_key = "key_" + secrets.token_hex(16)
        user_api_keys[chat_id] = new_key
        api_keys_db[new_key] = chat_id

        api_text, kb = get_api_text_and_kb(chat_id)
        bot.edit_message_text(api_text, chat_id, call.message.message_id, reply_markup=kb, parse_mode="Markdown")
        bot.answer_callback_query(call.id, "✅ API Kalit yangilandi!")

    elif call.data == "back_to_main":
        try: bot.delete_message(chat_id, call.message.message_id)
        except: pass
        bot.send_message(chat_id, "Asosiy menyu:", reply_markup=get_main_menu(chat_id))

    # --- ADMIN CALLBACKLARI ---
    elif call.data == "admin_create_promo" and chat_id in ADMINS:
        msg = bot.send_message(chat_id, "Promokod ma'lumotlarini quyidagicha kiriting:\n\n`KOD SUMMA ISHLATISH_SONI`\nMasalan: `BONUS5000 5000 10`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, save_new_promo)

    elif call.data == "admin_set_ref" and chat_id in ADMINS:
        msg = bot.send_message(chat_id, f"Hozirgi taklif bonusi: **{REFERRAL_BONUS_SUM:,} so'm**\nYangi summa miqdorini kiriting (masalan: 3000):", parse_mode="Markdown")
        bot.register_next_step_handler(msg, save_ref_sum)

    elif call.data == "admin_manage_admins" and chat_id in ADMINS:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("➕ Admin Qo'shish", callback_data="admin_add_new"))
        kb.add(InlineKeyboardButton("❌ Admin O'chirish", callback_data="admin_remove_old"))
        text = f"👑 **Adminlar ro'yxati:**\n" + "\n".join([f"• `{a}`" for a in ADMINS])
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

    elif call.data == "admin_add_new" and chat_id in ADMINS:
        msg = bot.send_message(chat_id, "Yangi adminning Telegram ID raqamini kiriting:")
        bot.register_next_step_handler(msg, save_new_admin)

    elif call.data == "admin_remove_old" and chat_id in ADMINS:
        msg = bot.send_message(chat_id, "O'chiriladigan adminning Telegram ID raqamini kiriting:")
        bot.register_next_step_handler(msg, remove_admin)

    elif call.data == "admin_edit_price" and chat_id in ADMINS:
        kb = InlineKeyboardMarkup()
        games_list = list(prices.keys())
        for idx, g_name in enumerate(games_list):
            kb.add(InlineKeyboardButton(f"{g_name}", callback_data=f"apg_{idx}"))
        bot.send_message(chat_id, "Bo'limni tanlang:", reply_markup=kb)

    elif call.data.startswith("apg_") and chat_id in ADMINS:
        g_idx = int(call.data.split("_")[1])
        g_name = list(prices.keys())[g_idx]
        kb = InlineKeyboardMarkup()
        cats_list = list(prices[g_name].keys())
        for c_idx, c_name in enumerate(cats_list):
            kb.add(InlineKeyboardButton(f"📁 {c_name}", callback_data=f"apc_{g_idx}_{c_idx}"))
        bot.send_message(chat_id, f"**{g_name}** kategroyasini tanlang:", parse_mode="Markdown", reply_markup=kb)

    elif call.data.startswith("apc_") and chat_id in ADMINS:
        parts = call.data.split("_")
        g_idx, c_idx = int(parts[1]), int(parts[2])
        g_name = list(prices.keys())[g_idx]
        c_name = list(prices[g_name].keys())[c_idx]
        
        kb = InlineKeyboardMarkup()
        items_list = list(prices[g_name][c_name].keys())
        for i_idx, i_name in enumerate(items_list):
            kb.add(InlineKeyboardButton(f"🏷 {i_name}", callback_data=f"api_{g_idx}_{c_idx}_{i_idx}"))
        bot.send_message(chat_id, "Mahsulotni tanlang:", reply_markup=kb)

    elif call.data.startswith("api_") and chat_id in ADMINS:
        parts = call.data.split("_")
        g_idx, c_idx, i_idx = int(parts[1]), int(parts[2]), int(parts[3])
        g_name = list(prices.keys())[g_idx]
        c_name = list(prices[g_name].keys())[c_idx]
        i_name = list(prices[g_name][c_name].keys())[i_idx]
        
        current_p = prices[g_name][c_name][i_name]
        msg = bot.send_message(chat_id, f"Mahsulot: **{i_name}**\nHozirgi narxi: **{current_p:,} so'm**\n\nYangi narxni kiriting:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, save_new_price, g_name, c_name, i_name)

    # --- BUYURTMA CALLBACKLARI ---
    elif call.data.startswith("game_"):
        g_idx = int(call.data.split("_")[1])
        game_name = list(prices.keys())[g_idx]
        user_data[chat_id] = {"game": game_name}
        
        keyboard = InlineKeyboardMarkup()
        for c_idx, category in enumerate(prices[game_name].keys()):
            keyboard.add(InlineKeyboardButton(f"📁 {category}", callback_data=f"cat_{g_idx}_{c_idx}"))
        bot.edit_message_text(f"Siz **{game_name}** ni tanladingiz.\nBo'limni tanlang:", chat_id, call.message.message_id, reply_markup=keyboard, parse_mode="Markdown")

    elif call.data.startswith("cat_"):
        parts = call.data.split("_")
        g_idx, c_idx = int(parts[1]), int(parts[2])
        game_name = list(prices.keys())[g_idx]
        category_name = list(prices[game_name].keys())[c_idx]
        user_data[chat_id]["category"] = category_name
        
        keyboard = InlineKeyboardMarkup()
        for i_idx, (item, price_val) in enumerate(prices[game_name][category_name].items()):
            keyboard.add(InlineKeyboardButton(f"{item} — {price_val:,} so'm", callback_data=f"item_{g_idx}_{c_idx}_{i_idx}"))
        keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"game_{g_idx}"))
        bot.edit_message_text("Mahsulotni tanlang:", chat_id, call.message.message_id, reply_markup=keyboard, parse_mode="Markdown")

    elif call.data.startswith("item_"):
        parts = call.data.split("_")
        g_idx, c_idx, i_idx = int(parts[1]), int(parts[2]), int(parts[3])
        game_name = list(prices.keys())[g_idx]
        category_name = list(prices[game_name].keys())[c_idx]
        item_name = list(prices[game_name][category_name].keys())[i_idx]
        
        user_data[chat_id]["item"] = item_name
        bot.edit_message_text(f"Tanlandi: **{item_name}**\n\nO'yindagi yoki Telegram **ID / Username** ingizni kiriting:", chat_id, call.message.message_id, parse_mode="Markdown")
        bot.register_next_step_handler(call.message, process_player_id)

    elif call.data == "topup_balance":
        bot.edit_message_text(f"💳 **Karta:** `{KARTA_RAQAMI}`\nEgasi: **{KARTA_EGASI}**\n\nSummani kiriting (masalan: `50000`):", chat_id, call.message.message_id, parse_mode="Markdown")
        bot.register_next_step_handler(call.message, process_topup_amount)

    elif call.data.startswith("approve_") or call.data.startswith("reject_"):
        if call.from_user.id not in ADMINS:
            bot.answer_callback_query(call.id, "Bu faqat adminlar uchun!", show_alert=True)
            return
            
        parts = call.data.split("_")
        action, target_user_id = parts[0], int(parts[1])
        
        if action == "approve":
            if target_user_id in pending_amounts:
                amount = pending_amounts[target_user_id]
                if target_user_id not in user_balances: user_balances[target_user_id] = {"balance": 0, "history": []}
                
                user_balances[target_user_id]["balance"] += amount
                user_balances[target_user_id]["history"].append(f"• Balans to'ldirildi: +{amount:,} so'm ✅")
                del pending_amounts[target_user_id]
                
                bot.edit_message_caption(f"{call.message.caption}\n\n✅ **STATUS: TASDIQLANDI**", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")
                try: bot.send_message(target_user_id, f"🎉 Hisobingizga **{amount:,} so'm** qo'shildi!", parse_mode="Markdown")
                except: pass
        else:
            if target_user_id in pending_amounts: del pending_amounts[target_user_id]
            bot.edit_message_caption(f"{call.message.caption}\n\n❌ **STATUS: RAD ETILDI**", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")
            try: bot.send_message(target_user_id, "❌ To'lov chekingiz rad etildi.", parse_mode="Markdown")
            except: pass

# ==================== STEP FUNKSIYALARI ====================
def save_new_promo(message):
    try:
        code, amount, uses = message.text.split()
        promo_codes[code.upper()] = {
            "amount": int(amount),
            "uses": int(uses),
            "used_by": []
        }
        bot.send_message(message.chat.id, f"✅ **Promokod Yaratildi!**\n\n🎟 Kod: `{code.upper()}`\n💰 Summa: **{int(amount):,} so'm**\n👥 Ishlatishlar soni: **{uses} ta**", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "❌ Noto'g'ri format! Format: `KOD SUMMA ISHLATISH_SONI`")

def process_use_promo(message):
    chat_id = message.chat.id
    code = message.text.strip().upper()
    
    if code in promo_codes:
        promo = promo_codes[code]
        if chat_id in promo["used_by"]:
            bot.send_message(chat_id, "⚠️ **Siz bu promokodni allaqachon ishlatgansiz!**")
        elif promo["uses"] <= 0:
            bot.send_message(chat_id, "⚠️ **Bu promokodning ishlatish limiti tugagan!**")
        else:
            promo["uses"] -= 1
            promo["used_by"].append(chat_id)
            amount = promo["amount"]
            
            if chat_id not in user_balances: user_balances[chat_id] = {"balance": 0, "history": []}
            user_balances[chat_id]["balance"] += amount
            user_balances[chat_id]["history"].append(f"• Promokod ({code}): +{amount:,} so'm 🎁")
            
            bot.send_message(chat_id, f"🎉 **Tabriklaymiz!**\nPromokod faollashtirildi: +**{amount:,} so'm** balansingizga qo'shildi!", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ **Bunday promokod mavjud emas!**")

def save_ref_sum(message):
    global REFERRAL_BONUS_SUM
    if message.text.isdigit():
        REFERRAL_BONUS_SUM = int(message.text)
        bot.send_message(message.chat.id, f"✅ Har bir taklif uchun pul bonusi **{REFERRAL_BONUS_SUM:,} so'm** ga o'zgartirildi!", parse_mode="Markdown")
    else: bot.send_message(message.chat.id, "❌ Raqam kiriting!")

def save_new_admin(message):
    if message.text.isdigit():
        new_id = int(message.text)
        if new_id not in ADMINS:
            ADMINS.append(new_id)
            bot.send_message(message.chat.id, f"✅ `{new_id}` adminlarga qo'shildi!", parse_mode="Markdown")
        else: bot.send_message(message.chat.id, "⚠️ Allaqachon admin!")
    else: bot.send_message(message.chat.id, "❌ Noto'g'ri ID!")

def remove_admin(message):
    if message.text.isdigit():
        old_id = int(message.text)
        if old_id in ADMINS:
            ADMINS.remove(old_id)
            bot.send_message(message.chat.id, f"✅ `{old_id}` adminlikdan olindi!", parse_mode="Markdown")
        else: bot.send_message(message.chat.id, "⚠️ Ro'yxatda yo'q!")
    else: bot.send_message(message.chat.id, "❌ Noto'g'ri ID!")

def save_new_price(message, game, cat, item):
    if message.text.isdigit():
        new_p = int(message.text)
        prices[game][cat][item] = new_p
        bot.send_message(message.chat.id, f"✅ **{item}** narxi **{new_p:,} so'm** ga o'zgartirildi!", parse_mode="Markdown")
    else: bot.send_message(message.chat.id, "❌ Faqat raqam kiriting!")

def process_topup_amount(message):
    chat_id = message.chat.id
    text = message.text
    if text and text.startswith('/'): return
    if not text.isdigit():
        bot.send_message(chat_id, "⚠️ Faqat raqam kiriting:")
        bot.register_next_step_handler(message, process_topup_amount)
        return
    user_data[chat_id] = {"topup_amount": int(text)}
    bot.send_message(chat_id, f"✅ Summa: **{int(text):,} so'm**.\nEndi **chek rasmini** yuboring:", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_topup_receipt)

def process_topup_receipt(message):
    chat_id = message.chat.id
    if message.content_type == 'photo':
        amount = user_data.get(chat_id, {}).get("topup_amount", 0)
        file_id = message.photo[-1].file_id
        pending_amounts[chat_id] = amount
        admin_markup = InlineKeyboardMarkup()
        admin_markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{chat_id}"), InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{chat_id}"))
        for adm in ADMINS:
            try: bot.send_photo(adm, file_id, caption=f"💳 **Yangi to'lov cheki!**\n👤 ID: `{chat_id}`\n💰 Summa: **{amount:,} so'm**", reply_markup=admin_markup, parse_mode="Markdown")
            except Exception as e: print(e)
        bot.reply_to(message, "✅ **Chekingiz adminga yuborildi!**", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "⚠️ Iltimos, **rasm** yuboring!")
        bot.register_next_step_handler(message, process_topup_receipt)

def process_player_id(message):
    chat_id = message.chat.id
    player_id = message.text
    if chat_id not in user_data: user_data[chat_id] = {}
    user_data[chat_id]["player_id"] = player_id
    
    game, category, item = user_data[chat_id].get("game"), user_data[chat_id].get("category"), user_data[chat_id].get("item")
    price = prices[game][category][item]
    
    if chat_id not in user_balances: user_balances[chat_id] = {"balance": 0, "history": []}
    current_balance = user_balances[chat_id]["balance"]
    
    if current_balance < price:
        bot.send_message(chat_id, f"⚠️ **Balansda yetarli mablag' yo'q!**\n💰 Balans: **{current_balance:,} so'm**\n📦 Narx: **{price:,} so'm**", reply_markup=get_main_menu(chat_id), parse_mode="Markdown")
        return
        
    user_balances[chat_id]["balance"] -= price
    user_balances[chat_id]["history"].append(f"• Buyurtma: {item} (-{price:,} so'm) ✅")
    
    # Do'st taklif qilganga belgilangan so'm miqdorida pul o'tadi
    if chat_id in referrers:
        ref_id = referrers[chat_id]
        bonus = REFERRAL_BONUS_SUM
        if ref_id not in user_balances: user_balances[ref_id] = {"balance": 0, "history": []}
        user_balances[ref_id]["balance"] += bonus
        user_balances[ref_id]["history"].append(f"• Referal pul bonusi: +{bonus:,} so'm 🎉")
        referral_earnings[ref_id] = referral_earnings.get(ref_id, 0) + bonus
        try: bot.send_message(ref_id, f"🎉 **Taklif bonusi!** Do'stingiz xaridi uchun **+{bonus:,} so'm** balansingizga qo'shildi.")
        except: pass

    success, msg = send_payerpin_order(item, player_id)
    
    for adm in ADMINS:
        try: bot.send_message(adm, f"🎮 **Yangi Buyurtma!**\n👤 ID: `{chat_id}`\n🕹 {game} - {item}\n🆔 Player ID/Username: `{player_id}`\n⚡ Holat: {msg}", parse_mode="Markdown")
        except: pass
        
    bot.send_message(chat_id, f"✅ **Buyurtmangiz qabul qilindi!**\n📦 Mahsulot: **{item}**\n💰 Qolgan balans: **{user_balances[chat_id]['balance']:,} so'm**", reply_markup=get_main_menu(chat_id), parse_mode="Markdown")

# ==================== PARALLEL RUN ====================
def start_bot():
    print("Bot ishga tushdi...")
    bot.infinity_polling()

def start_api():
    print("FastAPI ishga tushdi...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    t1 = threading.Thread(target=start_bot)
    t2 = threading.Thread(target=start_api)
    t1.start()
    t2.start()
