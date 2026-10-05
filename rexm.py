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
