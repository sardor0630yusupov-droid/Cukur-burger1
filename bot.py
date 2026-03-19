import telebot
from telebot import types
import config
import sqlite3
from datetime import datetime

bot = telebot.TeleBot(config.TOKEN)

# DATABASE
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    phone TEXT,
    lat TEXT,
    lon TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    items TEXT,
    total INTEGER,
    date TEXT
)
""")
conn.commit()

# MENU
menu = {
    "🍽 Milliy taomlar": [
        ("Somsa go'shtli",13000),
        ("Somsa kartoshka",10000),
        ("Somsa qovoq",10000)
    ],
    "🍟 Mix": [
        ("Shaverma",25000),
        ("Lavash obichniy",35000),
        ("Lavash sirniy",42000),
        ("Lavash dvaynoy",47000),
        ("Xaggi",32000),
        ("Xaggi sirli",47000),
        ("Toster go'shtli",35000),
        ("Toster tovuq",30000)
    ],
    "🍟 Fri": [
        ("Fri obichniy",15000),
        ("Fri sharik",15000)
    ],
    "☕ Coffee va ichimliklar": [
        ("Choy ko'k",3000),("Choy qora",3000),
        ("Choy qora limon",12000),("Choy bardak",20000),
        ("Espresso",15000),("Kapuchino",18000),
        ("Amerikano",15000),("Latte",22000),
        ("Ice latte",25000),("Raf",28000),
        ("Kakao",20000),("Goryachiy shokolad",25000),
        ("Imbirniy chay",25000),("Chay maloko",20000),
        ("Chernika chay",25000),("Malinali choy",25000),
        ("Oreo chizkeyk",35000),("Mango marakuya",35000),
        ("Qulupnay",35000)
    ],
    "🍔 Burger": [
        ("Burger obichniy",35000),
        ("Burger sirniy",40000),
        ("Burger dvaynoy",47000),
        ("Burger traynoy",57000),
        ("Burger combo (4X)",120000),
        ("Burger mini",25000),
        ("Kotlet",17000)
    ],
    "🌭 Xot Dog": [
        ("Xod dog obichniy",14000),
        ("Xod dog dvaynoy",16000),
        ("Xod dog sirniy",18000),
        ("Xod dog shashlichniy",32000),
        ("Xod dog traynoy",20000),
        ("Gigant xod dog",25000),
        ("Sosiska",3000)
    ],
    "🍕 Pizza": [
        ("Pizza peperoni",60000),
        ("Pizza asarti",75000),
        ("Pizza myasnoy",75000),
        ("Pizza kurinniy",65000)
    ]
}

cart = {}

# START
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("📞 Raqam yuborish", request_contact=True)
    markup.add(btn)
    bot.send_message(message.chat.id, "📞 Davom etish uchun raqamingizni yuboring:", reply_markup=markup)

# CONTACT
@bot.message_handler(content_types=['contact'])
def contact(message):
    cursor.execute("REPLACE INTO users VALUES (?,?,?,?)",
                   (message.chat.id, message.contact.phone_number, "", ""))
    conn.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("📍 Lokatsiya yuborish", request_location=True)
    markup.add(btn)
    bot.send_message(message.chat.id, "📍 Lokatsiyani yuboring:", reply_markup=markup)

# LOCATION
@bot.message_handler(content_types=['location'])
def location(message):
    cursor.execute("UPDATE users SET lat=?, lon=? WHERE user_id=?",
                   (message.location.latitude, message.location.longitude, message.chat.id))
    conn.commit()
    main_menu(message)

# MAIN MENU
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🍔 Menyu", "🛒 Savatcha")
    markup.add("📦 Mening buyurtmalarim", "📞 Murojaat uchun")
    bot.send_message(message.chat.id, "🏠 Asosiy menyu:", reply_markup=markup)

# MENYU
@bot.message_handler(func=lambda m: m.text == "🍔 Menyu")
def show_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cat in menu.keys():
        markup.add(cat)
    markup.add("🔙 Orqaga")
    bot.send_message(message.chat.id, "Bo‘lim tanlang:", reply_markup=markup)

# CATEGORY ITEMS
@bot.message_handler(func=lambda m: m.text in menu.keys())
def show_items(message):
    items = menu[message.text]
    text = f"📋 {message.text}:\n\n"
    for name, price in items:
        text += f"{name} - {price} so'm\n"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name, _ in items:
        markup.add(name)
    markup.add("🔙 Orqaga")
    bot.send_message(message.chat.id, text, reply_markup=markup)

# ADD TO CART
@bot.message_handler(func=lambda m: any(m.text == item[0] for cat in menu.values() for item in cat))
def add_cart(message):
    name = message.text
    price = next(price for cat in menu.values() for item, price in cat if item == name)
    cart.setdefault(message.chat.id, []).append((name, price))
    bot.send_message(message.chat.id, f"🛒 Qo‘shildi: {name}")

# CART
@bot.message_handler(func=lambda m: m.text == "🛒 Savatcha")
def show_cart(message):
    items = cart.get(message.chat.id, [])
    if not items:
        return bot.send_message(message.chat.id, "Savatcha bo‘sh")
    total = sum(i[1] for i in items)
    text = "🛒 Savatcha:\n\n"
    for i in items:
        text += f"{i[0]} - {i[1]}\n"
    text += f"\n💰 Jami: {total}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Buyurtma berish")
    bot.send_message(message.chat.id, text, reply_markup=markup)

# ORDER
@bot.message_handler(func=lambda m: m.text == "✅ Buyurtma berish")
def order(message):
    items = cart.get(message.chat.id, [])
    if not items:
        return

    total = sum(i[1] for i in items)
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    text_items = "\n".join([f"{i[0]} - {i[1]}" for i in items])

    # USER DATA
    cursor.execute("SELECT phone, lat, lon FROM users WHERE user_id=?", (message.chat.id,))
    phone, lat, lon = cursor.fetchone()

    # CHECK (USER + ADMIN + CHANNEL)
    check = f"""
🧾 CUKUR BURGER

📅 {date}

{text_items}

💰 Jami: {total}

📞 Telefon: {phone}

✅ Buyurtma qabul qilindi!
Tez orada siz bilan bog‘lanamiz. Aloqada bo‘ling.
"""

    # USERGA
    bot.send_message(message.chat.id, check)

    # SAVE ORDER
    cursor.execute("INSERT INTO orders (user_id, items, total, date) VALUES (?,?,?,?)",
                   (message.chat.id, text_items, total, date))
    conn.commit()

    # ADMINGA
    bot.send_message(config.ADMIN_ID, check)
    bot.send_location(config.ADMIN_ID, lat, lon)

    # KANALGA
    bot.send_message(config.ADMIN_CHANNEL, check)
    bot.send_location(config.ADMIN_CHANNEL, lat, lon)

    # CLEAR CART
    cart[message.chat.id] = []

# HISTORY
@bot.message_handler(func=lambda m: m.text == "📦 Mening buyurtmalarim")
def history(message):
    cursor.execute("SELECT items,total,date FROM orders WHERE user_id=?", (message.chat.id,))
    data = cursor.fetchall()
    if not data:
        return bot.send_message(message.chat.id, "Buyurtma yo‘q")
    for d in data:
        bot.send_message(message.chat.id, f"{d[2]}\n{d[0]}\n💰 {d[1]}")

# CONTACT
@bot.message_handler(func=lambda m: m.text == "📞 Murojaat uchun")
def contact_admin(message):
    bot.send_message(message.chat.id, "📞 Aloqa:\n+998912776767\n+998994506767")

# 🔙 ORQAGA
@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def go_back(message):
    main_menu(message)

bot.infinity_polling()