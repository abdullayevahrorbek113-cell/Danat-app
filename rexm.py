import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Tokeningiz
TOKEN = "8469058145:AAHDnKQfiS-isebvX8hHwrvSo6cuoEfaNfU"
bot = telebot.TeleBot(TOKEN)

# >>> O'ZINGIZNING TELEGRAM ID RAqAMINGIZ <<<
ADMIN_ID = 8622029343  
ADMIN_USERNAME = "@a_ahrorbek11"
KARTA_RAQAMI = "9860260115435265"
KARTA_EGASI = "Shamsiddinova A."

# Majburiy obuna kanali
REQUIRED_CHANNELS = ["@danatapp"]

# Narxlar bazasi
prices = {
    "Free Fire": {
        "Almazlar": {
            "110 Almaz": 12000,
            "341 Almaz": 35000,
            "572 Almaz": 58000,
            "1166 Almaz": 115000,
            "2398 Almaz": 230000,
            "6160 Almaz": 570000
        },
        "Propuski": {
            "Haftalik kichkina": 6000,
            "Evo Access 3 Kun": 9000,
            "Haftalik obuna": 23000,
            "Evo Access 7 Kun": 14000,
            "Oylik Obuna": 80000,
            "Evo Access 30 Kun": 42000
        },
        "Level Up": {
            "6 Level Up": 6000,
            "10 Level Up": 10000,
            "15 Level Up": 10000,
            "20 Level Up": 10000,
            "25 Level Up": 10000,
            "30 Level Up": 13000
        }
    },
    "PUBG Mobile": {
        "AVTO 24/7 (UC)": {
            "60 UC": 13000,
            "120 UC": 26000,
            "180 UC": 39000,
            "325 UC": 65000,
            "385 UC": 78000,
            "660 UC": 125000,
            "720 UC": 140000,
            "985 UC": 190000,
            "1320 UC": 250000,
            "1800 UC": 320000,
            "3850 UC": 640000,
            "8100 UC": 1300000
        },
        "To'plamlar (Prime)": {
            "1 Oy Prime": 16000,
            "3 Oy Prime": 45000,
            "6 Oy Prime": 80000,
            "12 Oy Prime": 160000,
            "1 Oy Prime Plus": 130000,
            "3 Oy Prime Plus": 390000,
            "6 Oy Prime Plus": 750000,
            "12 Oy Prime Plus": 1500000,
            "Nabor pervoy pokupki": 22000,
            "Nabor materialov": 50000,
            "Nabor mificheskiy": 70000,
            "Weekly Mythic Echo": 50000
        }
    },
    "Standoff 2": {
        "Gold": {
            "100 Gold": 20000,
            "500 Gold": 92000,
            "1000 Gold": 180000,
            "3000 Gold": 530000
        }
    },
    "Mobile Legends": {
        "Olmoslar": {
            "88 Olmos": 25000,
            "257 Olmos": 70000,
            "706 Olmos": 185000,
            "2195 Olmos": 550000
        }
    }
}

user_data = {}
user_balances = {}
pending_amounts = {}

def check_subscriptions(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            print(f"Obunani tekshirishda xatolik: {e}")
            return False
    return True

def get_subscription_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📢 Kanalga obuna bo'lish", url="https://t.me/danatapp"))
    keyboard.add(InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_sub"))
    return keyboard

def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🎮 Donat qilish"), KeyboardButton("💰 Mening hisobim"))
    markup.add(KeyboardButton("👤 Admin bilan bog'lanish"), KeyboardButton("📋 Narxlar va qoidalar"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    
    if not check_subscriptions(chat_id):
        bot.send_message(
            chat_id,
            "⚠️ **Botdan foydalanish uchun quyidagi kanalga obuna bo'lishingiz kerak:**",
            reply_markup=get_subscription_keyboard(),
            parse_mode="Markdown"
        )
        return

    if chat_id not in user_balances:
        user_balances[chat_id] = {"balance": 0, "history": []}
        
    bot.send_message(
        chat_id,
        f"Assalomu alaykum, **{message.from_user.first_name}**!\n\n"
        f"🆔 Sizning Telegram ID raqamingiz: `{chat_id}`\n\n"
        "🎮 Bizning botimiz orqali o'yinlarga tez va xavfsiz donat qiling.",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['payme'])
def add_balance(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "⚠️ Xato format! Ishlatilishi:\n`/payme [foydalanuvchi_id] [summa]`", parse_mode="Markdown")
        return
        
    target_user_id = int(args[1])
    amount = int(args[2])
    
    if target_user_id not in user_balances:
        user_balances[target_user_id] = {"balance": 0, "history": []}
        
    user_balances[target_user_id]["balance"] += amount
    user_balances[target_user_id]["history"].append(f"• Balansni to'ldirish: +{amount:,} so'm ✅")
    
    bot.reply_to(message, f"✅ Foydalanuvchi (`{target_user_id}`) balansiga **{amount:,} so'm** qo'shildi!\nJoriy balans: **{user_balances[target_user_id]['balance']:,} so'm**", parse_mode="Markdown")
    
    try:
        bot.send_message(
            target_user_id, 
            f"🎉 **Tabriklaymiz!**\n\nAdmin hisobingizni **{amount:,} so'm** bilan to'ldirdi.\n💰 Yangi balans: **{user_balances[target_user_id]['balance']:,} so'm**", 
            parse_mode="Markdown"
        )
    except:
        pass

@bot.message_handler(func=lambda message: message.text in ["🎮 Donat qilish", "💰 Mening hisobim", "👤 Admin bilan bog'lanish", "📋 Narxlar va qoidalar"])
def handle_menu(message):
    chat_id = message.chat.id
    
    if not check_subscriptions(chat_id):
        bot.send_message(
            chat_id,
            "⚠️ **Botdan foydalanish uchun quyidagi kanalga obuna bo'lishingiz kerak:**",
            reply_markup=get_subscription_keyboard(),
            parse_mode="Markdown"
        )
        return

    if chat_id not in user_balances:
        user_balances[chat_id] = {"balance": 0, "history": []}

    if message.text == "🎮 Donat qilish":
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔥 Free Fire", callback_data="game_Free Fire"))
        keyboard.add(InlineKeyboardButton("🎯 PUBG Mobile", callback_data="game_PUBG Mobile"))
        keyboard.add(InlineKeyboardButton("⚡ Standoff 2", callback_data="game_Standoff 2"))
        keyboard.add(InlineKeyboardButton("🛡 Mobile Legends", callback_data="game_Mobile Legends"))
        
        bot.send_message(chat_id, "Kerakli o'yinni tanlang:", reply_markup=keyboard)
        
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
        
    elif message.text == "👤 Admin bilan bog'lanish":
        bot.send_message(chat_id, f"Murojaat uchun admin: {ADMIN_USERNAME}")
        
    elif message.text == "📋 Narxlar va qoidalar":
        rules_text = (
            "📋 **Qoidalar va Ish tartibi:**\n\n"
            "1. O'yinni va kerakli mahsulotni tanlang.\n"
            "2. O'yin ID raqamingizni kiriting.\n"
            "3. Pul to'g'ridan-to'g'ri shaxsiy kabinetingiz balansidan yechiladi.\n"
            "4. Agar balansda mablag' yetarli bo'lmasa, 'Mening hisobim' orqali to'ldirib oling.\n\n"
            f"💳 Karta (Balansni to'ldirish uchun): `{KARTA_RAQAMI}` ({KARTA_EGASI})"
        )
        bot.send_message(chat_id, rules_text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if call.data == "check_sub":
        if check_subscriptions(chat_id):
            try:
                bot.delete_message(chat_id, call.message.message_id)
            except:
                pass
            bot.send_message(
                chat_id,
                "✅ Obunangiz tasdiqlandi! Asosiy menyudan foydalanishingiz mumkin.",
                reply_markup=get_main_menu()
            )
        else:
            bot.answer_callback_query(call.id, "⚠️ Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)
        return

    if not check_subscriptions(chat_id):
        bot.answer_callback_query(call.id, "⚠️ Avval kanalga obuna bo'ling!", show_alert=True)
        return
    
    if call.data.startswith("approve_") or call.data.startswith("reject_"):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Bu tugma faqat admin uchun!", show_alert=True)
            return
            
        parts = call.data.split("_")
        action = parts[0]
        target_user_id = int(parts[1])
        
        if action == "approve":
            if target_user_id in pending_amounts:
                amount = pending_amounts[target_user_id]
                if target_user_id not in user_balances:
                    user_balances[target_user_id] = {"balance": 0, "history": []}
                
                user_balances[target_user_id]["balance"] += amount
                user_balances[target_user_id]["history"].append(f"• Balans to'ldirildi: +{amount:,} so'm ✅")
                
                del pending_amounts[target_user_id]
                
                bot.edit_message_caption(
                    f"{call.message.caption}\n\n✅ **STATUS: TASDIQLANDI (Balans to'ldirildi)**",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    parse_mode="Markdown",
                    reply_markup=None
                )
                try:
                    bot.send_message(
                        target_user_id, 
                        f"🎉 **Tabriklaymiz!**\n\nAdmin to'lovingizni tasdiqladi va hisobingizga **{amount:,} so'm** qo'shildi!\n💰 Yangi balans: **{user_balances[target_user_id]['balance']:,} so'm**", 
                        parse_mode="Markdown"
                    )
                except:
                    pass
        else:
            if target_user_id in pending_amounts:
                del pending_amounts[target_user_id]
                
            bot.edit_message_caption(
                f"{call.message.caption}\n\n❌ **STATUS: RAD ETILDI**",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=None
            )
            try:
                bot.send_message(target_user_id, "❌ **Diqqat!** To'lov chekingiz admin tomonidan rad etildi.", parse_mode="Markdown")
            except:
                pass
        return

    if call.data == "topup_balance":
        bot.edit_message_text(
            f"💳 **Balansni to'ldirish uchun karta:**\n\n"
            f"`{KARTA_RAQAMI}`\n"
            f"Egasi: **{KARTA_EGASI}**\n\n"
            f"Iltimos, qancha summa o'tkazganingizni **raqamlarda kiriting** (masalan: `50000`):",
            chat_id, call.message.message_id, parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, process_topup_amount)
        
    elif call.data.startswith("game_"):
        game_name = call.data.split("_")[1]
        user_data[chat_id] = {"game": game_name}
        
        keyboard = InlineKeyboardMarkup()
        for category in prices[game_name].keys():
            keyboard.add(InlineKeyboardButton(f"📁 {category}", callback_data=f"cat_{game_name}_{category}"))
            
        bot.edit_message_text(f"Siz **{game_name}** ni tanladingiz.\n\nBo'limni tanlang:", chat_id, call.message.message_id, reply_markup=keyboard, parse_mode="Markdown")
        
    elif call.data.startswith("cat_"):
        parts = call.data.split("_")
        game_name = parts[1]
        category_name = parts[2]
        user_data[chat_id]["category"] = category_name
        
        keyboard = InlineKeyboardMarkup()
        for item, price_val in prices[game_name][category_name].items():
            keyboard.add(InlineKeyboardButton(f"{item} — {price_val:,} so'm", callback_data=f"item_{item}"))
            
        keyboard.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"game_{game_name}"))
        bot.edit_message_text(f"Mahsulotni tanlang:", chat_id, call.message.message_id, reply_markup=keyboard, parse_mode="Markdown")
        
    elif call.data.startswith("item_"):
        item_name = call.data.split("_")[1]
        user_data[chat_id]["item"] = item_name
        
        bot.edit_message_text(
            f"Tanlandi: **{item_name}**\n\n"
            "Iltimos, o'yindagi **ID raqamingizni** chatga yuboring:",
            chat_id, call.message.message_id, parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, process_player_id)

def process_topup_amount(message):
    chat_id = message.chat.id
    text = message.text
    
    if text and text.startswith('/'):
        if text.startswith('/start'):
            send_welcome(message)
        elif text.startswith('/payme') and chat_id == ADMIN_ID:
            add_balance(message)
        return

    if not text.isdigit():
        bot.send_message(chat_id, "⚠️ Iltimos, faqat raqamlarda summa kiriting (masalan: `50000`):")
        bot.register_next_step_handler(message, process_topup_amount)
        return
        
    amount = int(text)
    user_data[chat_id] = {"topup_amount": amount}
    
    bot.send_message(chat_id, f"✅ Summa: **{amount:,} so'm**.\nEndi to'lov **chekining rasmini (skrinshot)** yuboring:", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_topup_receipt)

def process_topup_receipt(message):
    chat_id = message.chat.id
    
    if message.text and message.text.startswith('/'):
        if message.text.startswith('/start'):
            send_welcome(message)
        return

    if message.content_type == 'photo':
        amount = user_data.get(chat_id, {}).get("topup_amount", 0)
        file_id = message.photo[-1].file_id
        
        pending_amounts[chat_id] = amount
        
        admin_markup = InlineKeyboardMarkup()
        admin_markup.add(
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{chat_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{chat_id}")
        )
        
        admin_text = (
            f"💳 **Yangi to'lov cheki (Balans to'ldirish)!**\n"
            f"👤 Foydalanuvchi ID: `{chat_id}`\n"
            f"💰 Summa: **{amount:,} so'm**"
        )
        try:
            bot.send_photo(ADMIN_ID, file_id, caption=admin_text, reply_markup=admin_markup, parse_mode="Markdown")
        except Exception as e:
            print(f"Adminga yuborishda xatolik: {e}")
        
        bot.reply_to(
            message, 
            f"✅ **Chekingiz adminga yuborildi!**\n\n"
            f"🔍 Admin tekshirib tasdiqlagach, balansingizga pul avtomatik qo'shiladi.", 
            parse_mode="Markdown"
        )
    else:
        bot.send_message(chat_id, "⚠️ Iltimos, to'lov cheki **rasmini (skrinshot)** yuboring!")
        bot.register_next_step_handler(message, process_topup_receipt)

def process_player_id(message):
    chat_id = message.chat.id
    player_id = message.text
    
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]["player_id"] = player_id
    
    game = user_data[chat_id].get("game")
    category = user_data[chat_id].get("category")
    item = user_data[chat_id].get("item")
    price = prices[game][category][item]
    
    if chat_id not in user_balances:
        user_balances[chat_id] = {"balance": 0, "history": []}
        
    current_balance = user_balances[chat_id]["balance"]
    
    if current_balance < price:
        bot.send_message(
            chat_id,
            f"⚠️ **Balansingizda yetarli mablag' yo'q!**\n\n"
            f"💰 Sizning balansingiz: **{current_balance:,} so'm**\n"
            f"📦 Mahsulot narxi: **{price:,} so'm**\n"
            f"❌ Yetishmayotgan summa: **{price - current_balance:,} so'm**\n\n"
            f"Iltimos, oldin 'Mening hisobim' orqali balansingizni to'ldiring.",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        return
        
    user_balances[chat_id]["balance"] -= price
    user_balances[chat_id]["history"].append(f"• Donat: {item} (-{price:,} so'm) ✅")
    
    admin_text = (
        f"🎮 **Yangi Donat Buyurtmasi (Balansdan to'landi)!**\n\n"
        f"👤 Foydalanuvchi ID: `{chat_id}`\n"
        f"🕹 O'yin: **{game}**\n"
        f"📦 Mahsulot: **{item}**\n"
        f"🆔 O'yin ID: `{player_id}`\n"
        f"💰 Narxi: **{price:,} so'm**"
    )
    
    try:
        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Adminga yuborishda xatolik: {e}")
        
    bot.send_message(
        chat_id,
        f"✅ **Buyurtmangiz qabul qilindi!**\n\n"
        f"📦 Mahsulot: **{item}**\n"
        f"🆔 O'yin ID: `{player_id}`\n"
        f"💰 Balansingizdan yechildi: **{price:,} so'm**\n"
        f"💰 Qolgan balans: **{user_balances[chat_id]['balance']:,} so'm**\n\n"
        f"🔍 Admin tez orada o'yinchingizga tashlab beradi.",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

print("Bot ishga tushdi...")
bot.infinity_polling()
