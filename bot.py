# -*- coding: utf-8 -*-
import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN = "8211708885:AAGe2GJOiYBzLrJPTpayrl2DOPXc7Mbw1qs"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CARD_NUMBER = "2200702056542769"

ADMIN_ID = 7203830273
users = set()

# хранение последнего сообщения бота
last_bot_messages = {}


# ---------- /start ----------
@bot.message_handler(commands=['start'])
def start(message):

    users.add(message.from_user.id)

    bot.send_message(
        message.chat.id,
        "Привет, ищешь кружки 18+ для сочной дрочки?😈"
    )

    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton("♾️ ДОСТУП НАВСЕГДА ♾️", callback_data="forever")
    btn2 = types.InlineKeyboardButton("📅 ДОСТУП НА МЕСЯЦ 📅", callback_data="month")

    markup.add(btn1)
    markup.add(btn2)

    bot.send_message(
        message.chat.id,
        "😍ЗДЕСЬ ТЫ НАЙДЕШЬ КРУЖКИ С ДОМАШКОЙ, ИНТИМКАМИ, ДРОЧКОЙ, И ВСЕМИ ВИДАМИ ЕБЛИ 💥❤️ВЫБЕРИТЕ ПОДХОДЯЩИЙ ТАРИФ:\n\n🆘 Помощь: @midll",
        reply_markup=markup
    )


# ---------- АДМИН ПАНЕЛЬ ----------
@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    text = "👤 Пользователи бота:\n\n"

    for user_id in users:
        try:
            user = bot.get_chat(user_id)
            username = user.username
            first_name = user.first_name

            text += f"Имя: {first_name}\n"
            text += f"Username: @{username if username else 'нет'}\n"
            text += f"ID: {user_id}\n\n"

        except:
            text += f"ID: {user_id}\n\n"

    bot.send_message(message.chat.id, text)


# ---------- СПАМ ----------
@bot.message_handler(commands=['spam'])
def spam(message):

    if message.from_user.id != ADMIN_ID:
        return

    for user_id in users:
        if user_id != ADMIN_ID:
            try:
                bot.send_message(user_id, "Все еще хочешь купить яблоки?")
            except:
                pass


# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    chat_id = call.message.chat.id

    # удалить прошлое сообщение бота
    if chat_id in last_bot_messages:
        try:
            bot.delete_message(chat_id, last_bot_messages[chat_id])
        except:
            pass

    if call.data == "forever":
        msg = send_payment(chat_id, "699.00₽")

    elif call.data == "month":
        msg = send_payment(chat_id, "299.00₽")

    elif call.data == "back":
        start(call.message)
        return

    else:
        return

    last_bot_messages[chat_id] = msg.message_id


# ---------- ОПЛАТА ----------
def send_payment(chat_id, price):

    text = f"""💳 Способ оплаты: Перевод
💸 К оплате: {price}

🏦 Карта: {CARD_NUMBER}

⭐ Оплатить звёздами:
https://t.me/+umjEbHsWQNMyMzJi"""

    markup = types.InlineKeyboardMarkup()

    # копирование в буфер обмена
    markup.add(
        types.InlineKeyboardButton(
            "💳 Скопировать карту",
            copy_text=types.CopyTextButton(text="2200702056542769")
        )
    )

    markup.add(types.InlineKeyboardButton("❌ Отменить", callback_data="back"))

    return bot.send_message(chat_id, text, reply_markup=markup)


# ---------- WEBHOOK ----------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def home():
    return "Bot is running", 200


# ---------- ЗАПУСК ----------
if __name__ == "__main__":

    bot.remove_webhook()
    bot.set_webhook(url=f"https://kenda-bot.onrender.com/{TOKEN}")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
