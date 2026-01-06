import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os
import datetime

# --- تنظیمات اصلی ---
API_TOKEN = '8356352784:AAHiddn8W2AByiedpQYEBNJxsCC4wqP2b-c'
ADMIN_ID = 7189522324  # آیدی عددی خودت
CHANNEL_ID = -1003630209623  # آیدی عددی کانالت

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- مدیریت پیام‌های ورودی ---
@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID and message.chat.id != CHANNEL_ID)
def handle_user_messages(message):
    user = message.from_user
    date = datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
    
    # گزارش کامل برای تو
    user_info = (
        f"📩 پیام جدید دریافت شد:\n\n"
        f"👤 نام: {user.first_name}\n"
        f"👤 فامیل: {user.last_name or 'ندارد'}\n"
        f"🆔 آیدی: {user.id}\n"
        f"username: @{user.username or 'ندارد'}\n"
        f"🌐 زبان: {user.language_code}\n"
        f"⏰ زمان: {date}\n"
        f"🔗 <b>لینک چت:</b> {user_link}\n"
        f"----------------------\n"
    )

    # ایجاد دکمه‌ها
    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton("✅ تایید و ارسال به کانال", callback_data=f"app_{message.chat.id}_{message.message_id}")
    reject_btn = types.InlineKeyboardButton("❌ رد کردن", callback_data=f"rej_{message.chat.id}_{message.message_id}")
    markup.add(approve_btn, reject_btn)

    if message.text:
        bot.send_message(ADMIN_ID, user_info + "متن پیام:\n" + message.text, reply_markup=markup)
    elif message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=user_info + "توضیحات عکس:\n" + (message.caption or "ندارد"), reply_markup=markup)
    
    bot.reply_to(message, "پیامت به دستم میرسه ممنون:) \n\nعموجویی")

# --- مدیریت دکمه‌ها ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data.split('_')
    action = data[0]
    u_id = data[1]
    m_id = data[2]

    if action == "app":
        try:
            # کپی پیام بدون اطلاعات اضافه به کانال
            bot.copy_message(CHANNEL_ID, u_id, m_id)
            bot.answer_callback_query(call.id, "به کانال ارسال شد ✅")
            bot.edit_message_caption(chat_id=ADMIN_ID, message_id=call.message.message_id, caption="این پیام تایید و ارسال شد. ✅") if call.message.photo else bot.edit_message_text("این پیام تایید و ارسال شد. ✅", chat_id=ADMIN_ID, message_id=call.message.message_id)
        except:
            bot.answer_callback_query(call.id, "خطا! ربات در کانال ادمین نیست.")

    elif action == "rej":
        bot.answer_callback_query(call.id, "پیام رد شد ❌")
        bot.delete_message(ADMIN_ID, call.message.message_id)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling()
    print("Bot and WebServer started...")
    bot.infinity_polling()
