import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os
import datetime
import pytz
import time

# ================= تنظیمات اختصاصی =================
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
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, "✅ <b>پنل مدیریت فعال شد.</b>", parse_mode='HTML')
    else:
        bot.reply_to(message, "سلام! پیامتو بفرست عموجویی میبینه.")

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'voice', 'video_note'])
def handle_all_messages(message):
    if message.chat.id == ADMIN_ID:
        return

    user = message.from_user
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.datetime.now(tehran_tz)
    date_str = now.strftime('%Y/%m/%d')
    time_str = now.strftime('%H:%M:%S')
    chat_link = f"tg://user?id={user.id}"
    
    # پیام اول: اطلاعات فوق کامل فرستنده
    user_info = (
        f"📩 <b>گزارش جدید دریافت شد</b>\n"
        f"--------------------------\n"
        f"👤 <b>نام:</b> {user.first_name}\n"
        f"👤 <b>نام خانوادگی:</b> {user.last_name or 'ندارد'}\n"
        f"🆔 <b>آیدی عددی:</b> <code>{user.id}</code>\n"
        f"🆔 <b>یوزرنیم:</b> @{user.username or 'ندارد'}\n"
        f"🌐 <b>زبان:</b> {user.language_code or 'نامشخص'}\n"
        f"📅 <b>تاریخ:</b> {date_str}\n"
        f"⏰ <b>ساعت (تهران):</b> {time_str}\n\n"
        f"🔗 <a href='{chat_link}'>ورود مستقیم به پی‌وی کاربر</a>\n"
        f"--------------------------"
    )

    # مرحله ۳: دکمه‌ها
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_app = types.InlineKeyboardButton("✅ تایید و انتشار", callback_data=f"app_{message.chat.id}_{message.message_id}")
    btn_rej = types.InlineKeyboardButton("❌ رد کردن و حذف", callback_data=f"rej_{message.chat.id}_{message.message_id}")
    markup.add(btn_app, btn_rej)

    try:
        # ۱. ارسال اطلاعات کامل (پیام اول)
        bot.send_message(ADMIN_ID, user_info, parse_mode='HTML')
        
        # ۲. فورواردِ پیام اصلی کاربر (پیام دوم)
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        
        # ۳. ارسال دکمه‌های مدیریت (پیام سوم)
        bot.send_message(ADMIN_ID, "📝 <b>مدیریت:</b> برای پیام بالا چه تصمیمی می‌گیرید؟", reply_markup=markup, parse_mode='HTML')
        
        # پاسخ به کاربر
        bot.reply_to(message, "✅پیام شماره دست عموجویی رسید .")
    except Exception as e:
        print(f"Error in 3-step system: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data.split('_')
    action, u_id, m_id = data[0], data[1], data[2]

    if action == "app":
        try:
            bot.copy_message(CHANNEL_ID, u_id, m_id)
            bot.answer_callback_query(call.id, "در کانال منتشر شد ✅")
            bot.edit_message_text("✅ <b>این گزارش منتشر شد.</b>", chat_id=ADMIN_ID, message_id=call.message.message_id, parse_mode='HTML')
        except:
            bot.answer_callback_query(call.id, "خطا در ارسال به کانال!")
            
    elif action == "rej":
        try:
            bot.edit_message_text("❌ <b>این گزارش رد و از لیست حذف شد.</b>", chat_id=ADMIN_ID, message_id=call.message.message_id, parse_mode='HTML')
            bot.answer_callback_query(call.id, "رد شد.")
        except: pass

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    print("--- 3-Step Full-Info Bot is Online ---")
    bot.infinity_polling(timeout=20, skip_pending=True)
