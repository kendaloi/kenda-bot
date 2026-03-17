# -*- coding: utf-8 -*-
import os
import telebot
from telebot import types
from flask import Flask, request
import threading

TOKEN = "8211708885:AAGe2GJOiYBzLrJPTpayrl2DOPXc7Mbw1qs"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CARD_NUMBER = "2200702056542769"

ADMIN_ID = 7203830273

# теперь храним данные пользователей
users = {}

last_bot_messages = {}


# ---------- СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЯ ----------
def save_user(message):
    if message.from_user.id == ADMIN_ID or message.from_user.is_bot:
        return

    users[message.from_user.id] = {
        "username": message.from_user.username,
        "name": message.from_user.first_name
    }


# ---------- УДАЛЕНИЕ ----------
def delete_last(chat_id):
    if chat_id in last_bot_messages:
        try:
            bot.delete_message(chat_id, last_bot_messages[chat_id])
        except:
            pass


# ---------- /start ----------
@bot.message_handler(commands=['start'])
def start(message):

    save_user(message)
    delete_last(message.chat.id)

    bot.send_message(
        message.chat.id,
        "Привет, ищешь кружки 18+ для сочной дрочки?😈"
    )

    markup = types.InlineKeyboardMarkup()

    # ОБЫЧНЫЕ ЦЕНЫ
    btn1 = types.InlineKeyboardButton("♾️ Навсегда — 699₽", callback_data="forever")
    btn2 = types.InlineKeyboardButton("📅 Месяц — 299₽", callback_data="month")

    markup.add(btn1)
    markup.add(btn2)

    msg = bot.send_message(
        message.chat.id,
        "😍ЗДЕСЬ ТЫ НАЙДЕШЬ КРУЖКИ С ДОМАШКОЙ, ИНТИМКАМИ, ДРОЧКОЙ, И ВСЕМИ ВИДАМИ ЕБЛИ 💥❤️ВЫБЕРИТЕ ПОДХОДЯЩИЙ ТАРИФ:\n\n🆘 Помощь: @midll",
        reply_markup=markup
    )

    last_bot_messages[message.chat.id] = msg.message_id


# ---------- АДМИН ----------
@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    text = f"👤 Пользователи бота: {len(users)}\n\n"

    for user_id, data in users.items():

        username = data["username"]
        name = data["name"]

        text += f"Имя: {name}\n"
        text += f"Username: @{username if username else 'нет'}\n"
        text += f"ID: {user_id}\n\n"

    bot.send_message(message.chat.id, text)


# ---------- SPAM ----------
@bot.message_handler(commands=['spam'])
def spam(message):

    if message.from_user.id != ADMIN_ID:
        return

    for user_id in users:

        markup = types.InlineKeyboardMarkup()

        # СКИДОЧНЫЕ ЦЕНЫ
        btn1 = types.InlineKeyboardButton(
            "♾️ Навсегда ♾️",
            callback_data="forever1"
        )

        btn2 = types.InlineKeyboardButton(
            "📅 Месяц 📆",
            callback_data="month1"
        )

        markup.add(btn1)
        markup.add(btn2)

        msg = bot.send_message(
            user_id,
            "Любимый ❤️, все еще хочешь купить VIP? У нас для тебя жаркая скидка которая тебе очень понравится 😉",
            reply_markup=markup
        )

        # автоудаление через 1 час
        threading.Timer(
            3600,
            lambda m=msg: bot.delete_message(m.chat.id, m.message_id)
        ).start()


# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    chat_id = call.message.chat.id

    delete_last(chat_id)

    if call.data == "forever":
        msg = send_payment(chat_id, "699₽")

    elif call.data == "month":
        msg = send_payment(chat_id, "299₽")

    elif call.data == "forever1":
        msg = send_payment(chat_id, "6̶9̶9̶₽̶ 499₽ СКИДКА!!!")

    elif call.data == "month1":
        msg = send_payment(chat_id, "2̶9̶9̶₽̶ 199₽ СКИДКА!!!")

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
