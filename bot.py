import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os
import datetime
import pytz
import time

# ================= تنظیمات اختصاصی شما =================
API_TOKEN = '8331070970:AAHquQria2TRCjkRBoauQo1BYKMlUWZztZg'
ADMIN_ID = 7189522324
CHANNEL_ID = -1003630209623
# ======================================================

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, "✅ <b>درود مدیریت!</b>\nربات آماده دریافت گزارش‌ها و فوروارد پیام کاربران است.", parse_mode='HTML')
    else:
        bot.reply_to(message, "سلام! پیام یا تصویر خود را بفرستید تا پس از تایید مدیریت، در کانال قرار بگیرد.")

@bot.message_handler(content_types=['text', 'photo', 'video', 'document'])
def handle_all_messages(message):
    # پیام‌های ادمین برای خودش فوروارد نشود
    if message.chat.id == ADMIN_ID:
        return

    user = message.from_user
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.datetime.now(tehran_tz)
    time_str = now.strftime('%H:%M:%S')
    chat_link = f"tg://user?id={user.id}"
    
    # آماده‌سازی اطلاعات فرستنده
    user_info = (
        f"📩 <b>اطلاعات فرستنده:</b>\n"
        f"👤 <b>نام:</b> {user.first_name} {user.last_name or ''}\n"
        f"🆔 <b>آیدی:</b> <code>{user.id}</code>\n"
        f"⏰ <b>ساعت:</b> {time_str}\n"
        f"🔗 <a href='{chat_link}'>ورود به پی‌وی کاربر</a>\n"
    )

    # ایجاد دکمه‌های تایید و رد
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_app = types.InlineKeyboardButton("✅ تایید و ارسال به کانال", callback_data=f"app_{message.chat.id}_{message.message_id}")
    btn_rej = types.InlineKeyboardButton("❌ رد کردن", callback_data=f"rej_{message.chat.id}_{message.message_id}")
    markup.add(btn_app, btn_rej)

    try:
        # ۱. ابتدا اطلاعات کاربر را همراه با دکمه‌ها برای ادمین می‌فرستیم
        bot.send_message(ADMIN_ID, user_info, reply_markup=markup, parse_mode='HTML')
        
        # ۲. بلافاصله پیام اصلی کاربر را برای ادمین فوروارد می‌کنیم
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        
        # ۳. پاسخ به کاربر
        bot.reply_to(message, "✅ پیام شما با موفقیت برای مدیریت ارسال شد.")
    except Exception as e:
        print(f"Error in forwarding: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data.split('_')
    action, u_id, m_id = data[0], data[1], data[2]

    if action == "app":
        try:
            # کپی پیام کاربر به کانال
            bot.copy_message(CHANNEL_ID, u_id, m_id)
            bot.answer_callback_query(call.id, "در کانال منتشر شد ✅")
            bot.edit_message_text("✅ این پیام تایید و به کانال فرستاده شد.", chat_id=ADMIN_ID, message_id=call.message.message_id)
        except Exception as e:
            bot.answer_callback_query(call.id, "خطا در ارسال به کانال!")
            print(f"Channel Copy Error: {e}")
            
    elif action == "rej":
        try:
            bot.edit_message_text("❌ این پیام توسط شما رد شد.", chat_id=ADMIN_ID, message_id=call.message.message_id)
            bot.answer_callback_query(call.id, "رد شد ❌")
        except:
            pass

if __name__ == "__main__":
    # اجرای وب‌سرور در ترد جداگانه
    Thread(target=run_flask, daemon=True).start()
    
    # پاکسازی تداخل‌های احتمالی
    bot.remove_webhook()
    time.sleep(1)
    
    print("--- Robot is Starting ---")
    # شروع به کار ربات به صورت هوشمند و بدون توقف
    bot.infinity_polling(timeout=20, skip_pending=True)
