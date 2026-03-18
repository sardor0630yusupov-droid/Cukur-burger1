from telebot import types

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🍔 Menyu")
    btn2 = types.KeyboardButton("🛒 Buyurtma berish")
    btn3 = types.KeyboardButton("📞 Aloqa")
    markup.add(btn1, btn2, btn3)
    return markup

def menu_buttons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🍔 Burger")
    btn2 = types.KeyboardButton("🥤 Ichimlik")
    btn3 = types.KeyboardButton("🔙 Orqaga")
    markup.add(btn1, btn2, btn3)
    return markup