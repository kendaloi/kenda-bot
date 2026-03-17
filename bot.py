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

    # КНОПКИ СТОЛБИКОМ
    markup.add(btn1)
    markup.add(btn2)

    bot.send_message(
        message.chat.id,
        "😍ЗДЕСЬ ТЫ НАЙДЕШЬ КРУЖКИ С ДОМАШКОЙ, ИНТИМКАМИ, ДРОЧКОЙ, И ВСЕМИ ВИДАМИ ЕБЛИ 💥❤️ВЫБЕРИТЕ ПОДХОДЯЩИЙ ТАРИФ:\n\n🆘 Помощь: @midll",
        reply_markup=markup
    )


# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    # ===== ТАРИФ НАВСЕГДА =====
    if call.data == "forever":
        send_payment(call.message.chat.id, "699.00₽")

    # ===== ТАРИФ НА МЕСЯЦ =====
    elif call.data == "month":
        send_payment(call.message.chat.id, "299.00₽")

    # ===== СКОПИРОВАТЬ КАРТУ =====
    elif call.data == "copy":
        bot.answer_callback_query(
            call.id,
            text=CARD_NUMBER,
            show_alert=True
        )

    # ===== НАЗАД =====
    elif call.data == "back":
        start(call.message)


# ---------- ОПЛАТА ----------
def send_payment(chat_id, price):

    text = f"""💳 Способ оплаты: Перевод
💸 К оплате: {price}

🏦 Карта: {CARD_NUMBER}

⭐ Оплатить звёздами:
https://t.me/+umjEbHsWQNMyMzJi"""

    markup = types.InlineKeyboardMarkup()

    # кнопки столбиком
    markup.add(types.InlineKeyboardButton("💳 Скопировать карту", callback_data="copy"))
    markup.add(types.InlineKeyboardButton("❌ Отменить", callback_data="back"))

    bot.send_message(chat_id, text, reply_markup=markup)


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
