# -*- coding: utf-8 -*-
import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import json

TOKEN = "8611580639:AAF18VM0OFmHmeumwI4L96_mdVCv1okAkCw"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CARD_NUMBER = "2200702056542769"
ADMIN_ID = 7203830273

users = {}
blocked_users = set()
last_bot_messages = {}
user_tariff = {}

# ---------- ЗАГРУЗКА ----------
def load_users():
    global users, blocked_users
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
            users = data.get("users", {})
            blocked_users = set(data.get("blocked", []))
    except:
        users = {}
        blocked_users = set()

# ---------- СОХРАНЕНИЕ ----------
def save_all():
    with open("users.json", "w") as f:
        json.dump({
            "users": users,
            "blocked": list(blocked_users)
        }, f)

# ---------- СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЯ ----------
def save_user(message):
    if message.from_user.id == ADMIN_ID or message.from_user.is_bot:
        return
    users[str(message.from_user.id)] = {
        "username": message.from_user.username,
        "name": message.from_user.first_name
    }
    save_all()

# ---------- УДАЛЕНИЕ ----------
def delete_last(chat_id):
    if chat_id in last_bot_messages:
        for msg_id in last_bot_messages[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
        last_bot_messages[chat_id] = []

# ---------- /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message)
    delete_last(message.chat.id)

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("♾️ Навсегда ♾️", callback_data="forever_699")
    btn2 = types.InlineKeyboardButton("📅 Месяц 📆", callback_data="month_299")
    markup.add(btn1, btn2)

    msg1 = bot.send_message(message.chat.id, "Привет, ищешь кружки 18+ для сочной дрочки?😈")
    msg2 = bot.send_message(
        message.chat.id,
        "😍ЗДЕСЬ ТЫ НАЙДЕШЬ КРУЖКИ С ДОМАШКОЙ, ИНТИМКАМИ, ДРОЧКОЙ, И ВСЕМИ ВИДАМИ ЕБЛИ 💥❤️ВЫБЕРИТЕ ПОДХОДЯЩИЙ ТАРИФ:\n\n🆘 Помощь: @midll",
        reply_markup=markup
    )
    last_bot_messages[message.chat.id] = [msg1.message_id, msg2.message_id]

# ---------- АДМИН ----------
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    active_users = [u for u in users if u not in blocked_users]
    text = f"👤 Пользователи бота: {len(active_users)}\n\n"

    for user_id in active_users:
        data = users[user_id]
        username = data["username"]
        name = data["name"]
        text += f"Имя: {name}\nUsername: @{username if username else 'нет'}\nID: {user_id}\n\n"

    bot.send_message(message.chat.id, text)

# ---------- СПАМ (текст, фото, видео) ----------
@bot.message_handler(content_types=['text', 'photo', 'video'])
def spam(message):
    if message.from_user.id != ADMIN_ID:
        return

    text = ""
    if message.content_type == 'text':
        if message.text.startswith("/spam"):
            text = message.text.replace("/spam", "").strip()
        else:
            return
    elif message.content_type in ['photo', 'video']:
        if message.caption and message.caption.startswith("/spam"):
            text = message.caption.replace("/spam", "").strip()
        else:
            return

    # кнопки
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("♾️ Навсегда ♾️ СКИДКА!!!", callback_data="forever_6̶9̶9̶₽̶ 499")
    btn2 = types.InlineKeyboardButton("📅 Месяц 📅 СКИДКА!!!", callback_data="month_2̶9̶9̶₽̶ 199")
    markup.add(btn1, btn2)

    for user_id in list(users.keys()):
        if user_id in blocked_users or int(user_id) == ADMIN_ID:
            continue

        try:
            if message.content_type == 'text':
                msg = bot.send_message(int(user_id), text, reply_markup=markup)
            elif message.content_type == 'photo':
                msg = bot.send_photo(int(user_id), message.photo[-1].file_id, caption=text, reply_markup=markup)
            elif message.content_type == 'video':
                msg = bot.send_video(int(user_id), message.video.file_id, caption=text, reply_markup=markup)

            threading.Timer(1800, lambda m=msg: bot.delete_message(m.chat.id, m.message_id)).start()

        except:
            blocked_users.add(user_id)
            save_all()

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    delete_last(chat_id)

    if call.data.startswith("forever"):
        price = call.data.split("_")[1] + "₽"
        user_tariff[chat_id] = price
        msg = send_payment(chat_id, price)

    elif call.data.startswith("month"):
        price = call.data.split("_")[1] + "₽"
        user_tariff[chat_id] = price
        msg = send_payment(chat_id, price)

    elif call.data == "retry":
        price = user_tariff.get(chat_id, "699₽")
        msg = send_payment(chat_id, price)

    elif call.data == "cancel":
        start(call.message)
        return

    elif call.data == "back":
        start(call.message)
        return

    elif call.data == "paid":
        clocks = ["🕛","🕐","🕑","🕒","🕓","🕔","🕕","🕖","🕗","🕘","🕙","🕚"]
        msg_anim = bot.send_message(chat_id, "🕛 Проверка платежа...")

        for i in range(33):
            try:
                bot.edit_message_text(f"{clocks[i % len(clocks)]} Проверка платежа...", chat_id, msg_anim.message_id)
                time.sleep(0.3)
            except:
                pass

        try:
            bot.delete_message(chat_id, msg_anim.message_id)
        except:
            pass

        markup = types.InlineKeyboardMarkup()
        retry = types.InlineKeyboardButton("Повторить 🔁", callback_data="retry")
        cancel = types.InlineKeyboardButton("Отмена ❌", callback_data="cancel")
        markup.add(retry, cancel)

        msg = bot.send_message(chat_id,
            "Извините, но платеж не прошел или пришла не вся сумма за выбранный тариф. 🙁\n\nПовторите платеж пожалуйста. 🙏",
            reply_markup=markup
        )
    else:
        return

    last_bot_messages[chat_id] = [msg.message_id]

# ---------- ОПЛАТА ----------
def send_payment(chat_id, price):
    text = f"""💳 Способ оплаты: Перевод
💸 К оплате: {price}

🏦 Карта: {CARD_NUMBER}

⭐ Оплатить звёздами:
https://t.me/+umjEbHsWQNMyMzJi"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Скопировать карту", copy_text=types.CopyTextButton(text="2200702056542769")))
    markup.add(types.InlineKeyboardButton("✅ Я ОПЛАТИЛ", callback_data="paid"))
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
    load_users()
    bot.remove_webhook()
    bot.set_webhook(url=f"https://kenda-bot.onrender.com/{TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
