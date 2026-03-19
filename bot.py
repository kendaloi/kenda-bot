# -*- coding: utf-8 -*-
import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import json
import math
import schedule

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
        json.dump({"users": users, "blocked": list(blocked_users)}, f)

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

# ---------- /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("♾️ Навсегда ♾️", callback_data="forever_699")
    )
    markup.add(
        types.InlineKeyboardButton("📅 Месяц 📆", callback_data="month_299")
    )

    bot.send_message(message.chat.id, "Привет, ищешь кружки 18+ для сочной дрочки?😈")
    bot.send_message(
        message.chat.id,
        "😍ЗДЕСЬ ТЫ НАЙДЕШЬ КРУЖКИ...\n\n🆘 Помощь: @midll",
        reply_markup=markup
    )

# ---------- /admin ----------
def generate_admin_text(page=1):
    user_list = list(users.keys())
    start_idx = (page-1)*USERS_PER_PAGE
    end_idx = start_idx + USERS_PER_PAGE

    text = f"👥 Всего пользователей: {len(users)}\n\n"

    for user_id in user_list[start_idx:end_idx]:
        data = users[user_id]
        blocked = "🚫 Заблокирован 🚫" if user_id in blocked_users else ""
        text += f"{blocked}\nИмя: {data['name']}\n@{data['username'] or 'нет'}\nID: {user_id}\n\n"

    return text, max(1, math.ceil(len(user_list)/USERS_PER_PAGE))

def generate_admin_markup(page, total):
    markup = types.InlineKeyboardMarkup()

    prev_page = page-1 if page>1 else total
    next_page = page+1 if page<total else 1

    markup.add(
        types.InlineKeyboardButton("⬅️", callback_data=f"admin_{prev_page}"),
        types.InlineKeyboardButton(f"{page}", callback_data="ignore"),
        types.InlineKeyboardButton("➡️", callback_data=f"admin_{next_page}")
    )

    markup.add(
        types.InlineKeyboardButton("🚫 Удалить 🚫", callback_data="delete_blocked"),
        types.InlineKeyboardButton("✉️ Удалить ✉️", callback_data="delete_msg")
    )

    return markup

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id != ADMIN_ID:
        return

    text, total = generate_admin_text(1)
    bot.send_message(message.chat.id, text, reply_markup=generate_admin_markup(1, total))

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    data = call.data

    bot.answer_callback_query(call.id)

    # ADMIN
    if data.startswith("admin_"):
        page = int(data.split("_")[1])
        text, total = generate_admin_text(page)
        bot.edit_message_text(text, chat_id, call.message.message_id,
                              reply_markup=generate_admin_markup(page, total))
        return

    if data == "delete_blocked":
        for uid in list(blocked_users):
            users.pop(uid, None)
        blocked_users.clear()
        save_all()
        text, total = generate_admin_text(1)
        bot.edit_message_text(text, chat_id, call.message.message_id,
                              reply_markup=generate_admin_markup(1, total))
        return

    if data == "delete_msg":
        bot.delete_message(chat_id, call.message.message_id)
        return

    if data == "ignore":
        return

    # ТАРИФ
    if data.startswith("forever") or data.startswith("month"):
        price = data.split("_")[1] + "₽"
        user_tariff[chat_id] = price

        bot.delete_message(chat_id, call.message.message_id)
        send_payment(chat_id, price)
        return

    # ОПЛАТА
    if data == "paid":
        msg = bot.send_message(chat_id, "🕛 Проверка платежа...")
        time.sleep(2)
        bot.delete_message(chat_id, msg.message_id)

        send_payment(chat_id, user_tariff.get(chat_id, "699₽"))
        return

    if data == "back":
        bot.delete_message(chat_id, call.message.message_id)
        start(call.message)

# ---------- ОПЛАТА ----------
def send_payment(chat_id, price):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Я ОПЛАТИЛ", callback_data="paid"))
    markup.add(types.InlineKeyboardButton("❌ Отменить", callback_data="back"))

    bot.send_message(chat_id, f"💳 К оплате: {price}\n\nКарта: {CARD_NUMBER}", reply_markup=markup)

# ---------- /spam ----------
@bot.message_handler(content_types=['text','photo','video'])
def spam(message):
    if message.from_user.id != ADMIN_ID:
        return

    if message.content_type == "text" and not message.text.startswith("/spam"):
        return

    text = message.text.replace("/spam","") if message.content_type=="text" else message.caption.replace("/spam","")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("♾️ Навсегда ♾️", callback_data="forever_699"))
    markup.add(types.InlineKeyboardButton("📅 Месяц 📆", callback_data="month_299"))

    for uid in list(users.keys()):
        if uid in blocked_users:
            continue
        try:
            if message.content_type == "text":
                msg = bot.send_message(int(uid), text, reply_markup=markup)
            elif message.content_type == "photo":
                msg = bot.send_photo(int(uid), message.photo[-1].file_id, caption=text, reply_markup=markup)
            else:
                msg = bot.send_video(int(uid), message.video.file_id, caption=text, reply_markup=markup)

            threading.Timer(1800, lambda m=msg: bot.delete_message(m.chat.id, m.message_id)).start()

        except:
            blocked_users.add(uid)
            save_all()

# ---------- ПРОВЕРКА ----------
def check_blocked():
    for uid in list(users.keys()):
        try:
            msg = bot.send_message(int(uid), ".")
            threading.Timer(1, lambda m=msg: bot.delete_message(m.chat.id, m.message_id)).start()
        except:
            blocked_users.add(uid)
            save_all()

def scheduler():
    schedule.every().day.at("12:00").do(check_blocked)
    while True:
        schedule.run_pending()
        time.sleep(30)

threading.Thread(target=scheduler, daemon=True).start()

# ---------- WEBHOOK ----------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "ok"

# ---------- START ----------
if __name__ == "__main__":
    load_users()
    bot.remove_webhook()
    bot.set_webhook(url=f"https://kenda-bot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
