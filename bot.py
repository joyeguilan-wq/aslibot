import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os
import datetime

# --- تنظیمات اصلی ---
API_TOKEN = '8356352784:AAHvGe0735LNpjeprxm73tNS0I35NDfwchk'
ADMIN_ID = 7189522324 # آیدی عددی خودت
CHANNEL_ID = -1003630209623 # آیدی عددی یا یوزرنیم کانال

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ربات بیدار است. پیام خود را بفرستید.")

@bot.message_handler(content_types=['text', 'photo'])
def handle_all_messages(message):
    if message.chat.id == ADMIN_ID:
        return

    user = message.from_user
    date = datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
    
    # اسم این متغیر رو دقیقاً گذاشتیم chat_link
    chat_link = f"tg://user?id={user.id}"
    
    user_info = (
        f"📩 *پیام جدید دریافت شد:*\n\n"
        f"👤 نام: {user.first_name}\n"
        f"👤 فامیل: {user.last_name or 'ندارد'}\n"
        f"🆔 آیدی: `{user.id}`\n"
        f"username: @{user.username or 'ندارد'}\n"
        f"🌐 زبان: {user.language_code}\n"
        f"⏰ زمان: {date}\n\n"
        f"🔗 [لینک چت مستقیم با کاربر]({chat_link})\n" # اینجا هم از همون اسم استفاده کردیم
        f"----------------------\n"
    )

    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton("✅ تایید و ارسال به کانال", callback_data=f"app_{message.chat.id}_{message.message_id}")
    reject_btn = types.InlineKeyboardButton("❌ رد کردن", callback_data=f"rej_{message.chat.id}_{message.message_id}")
    markup.add(approve_btn, reject_btn)

    try:
        if message.text:
            bot.send_message(ADMIN_ID, user_info + "متن پیام:\n" + message.text, reply_markup=markup, parse_mode='Markdown')
        elif message.photo:
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=user_info + "توضیحات عکس:\n" + (message.caption or "ندارد"), reply_markup=markup, parse_mode='Markdown')
        
        bot.reply_to(message, "ممنون:) از طرف عموجویی.")
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data.split('_')
    if data[0] == "app":
        try:
            bot.copy_message(CHANNEL_ID, data[1], data[2])
            bot.answer_callback_query(call.id, "به کانال ارسال شد ✅")
            text = "این پیام تایید و ارسال شد. ✅"
            if call.message.photo:
                bot.edit_message_caption(text, chat_id=ADMIN_ID, message_id=call.message.message_id)
            else:
                bot.edit_message_text(text, chat_id=ADMIN_ID, message_id=call.message.message_id)
        except:
            bot.answer_callback_query(call.id, "خطا در ارسال به کانال!")
    elif data[0] == "rej":
        bot.delete_message(ADMIN_ID, call.message.message_id)
        bot.answer_callback_query(call.id, "پیام رد شد ❌")

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling(none_stop=True)
