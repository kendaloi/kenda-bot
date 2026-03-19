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

# ---------- Загрузка пользователей ----------
def load_users():
    global users, blocked_users
    if not os.path.exists("users.json"):
        users = {}
        blocked_users = set()
        return
    try:
        with open("users.json", "r") as f:
            data = json.load(f)
            users = data.get("users", {})
            blocked_users = set(data.get("blocked", []))
    except:
        pass

def save_all():
    with open("users.json", "w") as f:
        json.dump({
            "users": users,
            "blocked": list(blocked_users)
        }, f)

# ---------- Сохранение пользователя ----------
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

# ---------- Удаление сообщений ----------
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
    markup.add(types.InlineKeyboardButton("♾️ Навсегда ♾️", callback_data="forever_699"))
    markup.add(types.InlineKeyboardButton("📅 Месяц 📆", callback_data="month_299"))

    msg1 = bot.send_message(message.chat.id, "Привет, ищешь кружки 18+ для сочной дрочки?😈")
    msg2 = bot.send_message(
        message.chat.id,
        "😍ЗДЕСЬ ТЫ НАЙДЕШЬ КРУЖКИ С ДОМАШКОЙ, ИНТИМКАМИ, ДРОЧКОЙ, И ВСЕМИ ВИДАМИ ЕБЛИ 💥❤️ВЫБЕРИТЕ ПОДХОДЯЩИЙ ТАРИФ:\n\n🆘 Помощь: @midll",
        reply_markup=markup
    )
    last_bot_messages[message.chat.id] = [msg1.message_id, msg2.message_id]

# ---------- /run ----------
@bot.message_handler(commands=['run'])
def run_animation(message):
    if message.from_user.id != ADMIN_ID:
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Удалить ❌", callback_data="delete_run"))

    msg = bot.send_message(message.chat.id, "🕛 Бесконечная загрузка", reply_markup=markup)

    thread = threading.Thread(target=animate_loading, args=(message.chat.id, msg.message_id))
    thread.daemon = True
    thread.start()

def animate_loading(chat_id, message_id):
    clocks = ["🕛","🕐","🕑","🕒","🕓","🕔","🕧","🕖","🕗","🕘","🕙","🕚"]

    start_time = time.time()
    duration = 86400

    i = 0
    while time.time() - start_time < duration:
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Удалить ❌", callback_data="delete_run"))

            bot.edit_message_text(
                f"{clocks[i % len(clocks)]} Бесконечная загрузка",
                chat_id,
                message_id,
                reply_markup=markup
            )

            time.sleep(2)  # безопасный интервал
            i += 1

        except Exception as e:
            if "Too Many Requests" in str(e):
                time.sleep(5)
                continue
            break

# ---------- /admin ----------
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
    text, total_pages = generate_admin_text(1)
    markup = generate_admin_markup(1, total_pages)
    msg = bot.send_message(message.chat.id, text, reply_markup=markup)
    last_bot_messages[message.chat.id] = [msg.message_id]

# ---------- /spam ----------
def delete_later(chat_id, message_id):
    time.sleep(1800)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

@bot.message_handler(content_types=['text','photo','video'])
def spam(message):
    if message.from_user.id != ADMIN_ID:
        return

    text = ""
    if message.content_type == 'text' and message.text.startswith("/spam"):
        text = message.text.replace("/spam","").strip()
    elif message.caption and message.caption.startswith("/spam"):
        text = message.caption.replace("/spam","").strip()
    else:
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("♾️ Навсегда ♾️ СКИДКА!!!", callback_data="forever_699"))
    markup.add(types.InlineKeyboardButton("📅 Месяц 📆 СКИДКА!!!", callback_data="month_299"))

    for user_id in users:
        if int(user_id) == ADMIN_ID or user_id in blocked_users:
            continue
        try:
            if message.content_type == 'text':
                msg = bot.send_message(int(user_id), text, reply_markup=markup)
            elif message.content_type == 'photo':
                msg = bot.send_photo(int(user_id), message.photo[-1].file_id, caption=text, reply_markup=markup)
            elif message.content_type == 'video':
                msg = bot.send_video(int(user_id), message.video.file_id, caption=text, reply_markup=markup)

            t = threading.Thread(target=delete_later, args=(msg.chat.id, msg.message_id))
            t.daemon = True
            t.start()

        except:
            blocked_users.add(user_id)
            save_all()

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data

    if data == "delete_run":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        return

    if data.startswith("admin_page_") or data in ["delete_blocked","delete_message","ignore"]:
        if data.startswith("admin_page_"):
            page = int(data.split("_")[-1])
            text, total_pages = generate_admin_text(page)
            markup = generate_admin_markup(page, total_pages)
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)
        elif data == "delete_blocked":
            for user_id in list(blocked_users):
                users.pop(user_id, None)
            blocked_users.clear()
            save_all()
        elif data == "delete_message":
            bot.delete_message(chat_id, call.message.message_id)
        return

    delete_last(chat_id)

    if data.startswith("forever"):
        price = data.split("_")[1] + "₽"
        msg = send_payment(chat_id, price)
    elif data.startswith("month"):
        price = data.split("_")[1] + "₽"
        msg = send_payment(chat_id, price)

    last_bot_messages[chat_id] = [msg.message_id]

# ---------- Оплата ----------
def send_payment(chat_id, price):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Скопировать карту", copy_text=types.CopyTextButton(text=CARD_NUMBER)))
    markup.add(types.InlineKeyboardButton("❌ Отменить", callback_data="back"))
    return bot.send_message(chat_id, f"💳 Способ оплаты\n💸 {price}\n\n{CARD_NUMBER}", reply_markup=markup)

# ---------- WEBHOOK ----------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def home():
    return "Bot is running", 200

if __name__ == "__main__":
    load_users()
    bot.remove_webhook()
    bot.set_webhook(url=f"https://kenda-bot.onrender.com/{TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
