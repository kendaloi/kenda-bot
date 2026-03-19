# -*- coding: utf-8 -*-
import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import json
import math

TOKEN = "8611580639:AAF18VM0OFmHmeumwI4L96_mdVCv1okAkCw"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

CARD_NUMBER = "2200702056542769"
ADMIN_ID = 7203830273

users = {}
blocked_users = set()
last_bot_messages = {}
user_tariff = {}

USERS_PER_PAGE = 10

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
    user_id = str(message.from_user.id)
    users[user_id] = {
        "username": message.from_user.username,
        "name": message.from_user.first_name
    }
    if user_id in blocked_users:
        blocked_users.remove(user_id)
    save_all()

# ---------- УДАЛЕНИЕ СООБЩЕНИЙ ----------
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
    markup.add(btn1)
    markup.add(btn2)

    msg1 = bot.send_message(message.chat.id, "Привет, ищешь кружки 18+ для сочной дрочки?😈")
    msg2 = bot.send_message(
        message.chat.id,
        "😍ЗДЕСЬ ТЫ НАЙДЕШЬ КРУЖКИ С ДОМАШКОЙ, ИНТИМКАМИ, ДРОЧКОЙ, И ВСЕМИ ВИДАМИ ЕБЛИ 💥❤️ВЫБЕРИТЕ ПОДХОДЯЩИЙ ТАРИФ:\n\n🆘 Помощь: @midll",
        reply_markup=markup
    )
    last_bot_messages[message.chat.id] = [msg1.message_id, msg2.message_id]

# ---------- /admin с пагинацией ----------
def generate_admin_text(page=1):
    active_users_list = list(users.keys())
    start_idx = (page-1)*USERS_PER_PAGE
    end_idx = start_idx + USERS_PER_PAGE
    subset = active_users_list[start_idx:end_idx]

    text = f"👥 Всего пользователей: {len(users)}\n\n"
    for user_id in subset:
        data = users[user_id]
        name = data["name"]
        username = data["username"] or "нет"
        blocked_note = "🚫 Заблокирован 🚫" if user_id in blocked_users else ""
        text += f"{blocked_note}\nИмя: {name}\nUsername: @{username}\nID: {user_id}\n\n"
    return text, max(1, math.ceil(len(active_users_list)/USERS_PER_PAGE))

def generate_admin_markup(page, total_pages):
    markup = types.InlineKeyboardMarkup()
    prev_page = page-1 if page>1 else total_pages
    next_page = page+1 if page<total_pages else 1

    markup.add(
        types.InlineKeyboardButton("⬅️", callback_data=f"admin_page_{prev_page}"),
        types.InlineKeyboardButton(f"{page}", callback_data="ignore"),
        types.InlineKeyboardButton("➡️", callback_data=f"admin_page_{next_page}")
    )
    markup.add(
        types.InlineKeyboardButton("🚫 Удалить 🚫", callback_data="delete_blocked"),
        types.InlineKeyboardButton("✉️ Удалить ✉️", callback_data="delete_message")
    )
    return markup

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    page = 1
    text, total_pages = generate_admin_text(page)
    markup = generate_admin_markup(page, total_pages)
    msg = bot.send_message(message.chat.id, text, reply_markup=markup)
    last_bot_messages[message.chat.id] = [msg.message_id]

# ---------- /spam (текст, фото, видео) ----------
@bot.message_handler(content_types=['text','photo','video'])
def spam(message):
    if message.from_user.id != ADMIN_ID:
        return

    text = ""
    content_type = message.content_type

    if content_type == 'text' and message.text.startswith("/spam"):
        text = message.text.replace("/spam","").strip()
    elif content_type in ['photo','video'] and message.caption and message.caption.startswith("/spam"):
        text = message.caption.replace("/spam","").strip()
    else:
        return

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("♾️ Навсегда ♾️ СКИДКА!!!", callback_data="forever_699")
    btn2 = types.InlineKeyboardButton("📅 Месяц 📆 СКИДКА!!!", callback_data="month_299")
    markup.add(btn1)
    markup.add(btn2)

    for user_id_str in list(users.keys()):
        if int(user_id_str) == ADMIN_ID or user_id_str in blocked_users:
            continue
        try:
            if content_type == 'text':
                msg = bot.send_message(int(user_id_str), text, reply_markup=markup)
            elif content_type == 'photo':
                msg = bot.send_photo(int(user_id_str), message.photo[-1].file_id, caption=text, reply_markup=markup)
            elif content_type == 'video':
                msg = bot.send_video(int(user_id_str), message.video.file_id, caption=text, reply_markup=markup)

            threading.Timer(1800, lambda m=msg: bot.delete_message(m.chat.id, m.message_id)).start()
        except:
            blocked_users.add(user_id_str)
            save_all()

# ---------- ОБЪЕДИНЁННЫЙ CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data

    # ---------- АДМИН ----------
    if data.startswith("admin_page_") or data in ["delete_blocked","delete_message","ignore"]:
        if data.startswith("admin_page_"):
            page = int(data.split("_")[-1])
            text, total_pages = generate_admin_text(page)
            markup = generate_admin_markup(page, total_pages)
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)
        elif data == "delete_blocked":
            for user_id in list(blocked_users):
                if user_id in users:
                    del users[user_id]
            blocked_users.clear()
            save_all()
            text, total_pages = generate_admin_text(1)
            markup = generate_admin_markup(1, total_pages)
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)
        elif data == "delete_message":
            try:
                bot.delete_message(chat_id, call.message.message_id)
            except:
                pass
        elif data == "ignore":
            pass
        return  # завершение обработки админских кнопок

    # ---------- ОПЛАТА / ТАРИФ ----------
    if data.startswith("forever"):
        price = data.split("_")[1] + "₽"
        user_tariff[chat_id] = price
        msg = send_payment(chat_id, price)
    elif data.startswith("month"):
        price = data.split("_")[1] + "₽"
        user_tariff[chat_id] = price
        msg = send_payment(chat_id, price)
    elif data == "retry":
        price = user_tariff.get(chat_id, "699₽")
        msg = send_payment(chat_id, price)
    elif data == "cancel" or data == "back":
        start(call.message)
        return
    elif data == "paid":
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
        markup.add(types.InlineKeyboardButton("Повторить 🔁", callback_data="retry"))
        markup.add(types.InlineKeyboardButton("Отмена ❌", callback_data="cancel"))
        msg = bot.send_message(chat_id,
            "Извините, но платеж не прошел или пришла не вся сумма за выбранный тариф. 🙁\n\nПовторите платеж пожалуйста. 🙏",
            reply_markup=markup
        )
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
