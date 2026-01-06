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
        bot.reply_to(message, "✅ <b>پنل مدیریت فعال است.</b>", parse_mode='HTML')
    else:
        bot.reply_to(message, "سلام! پیام یا تصویر خود را بفرستید تا پس از تایید مدیریت، در کانال قرار بگیرد.")

@bot.message_handler(content_types=['text', 'photo', 'video', 'document'])
def handle_all_messages(message):
    if message.chat.id == ADMIN_ID:
        return

    user = message.from_user
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.datetime.now(tehran_tz)
    time_str = now.strftime('%H:%M')
    chat_link = f"tg://user?id={user.id}"
    
    # قالب کامل اطلاعات فرستنده
    user_info = (
        f"👤 <b>فرستنده:</b> {user.first_name} {user.last_name or ''}\n"
        f"🆔 <b>آیدی:</b> <code>{user.id}</code>\n"
        f"⏰ <b>ساعت:</b> {time_str}\n"
        f"🔗 <a href='{chat_link}'>ورود به پی‌وی کاربر</a>\n"
        f"--------------------------\n"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_app = types.InlineKeyboardButton("✅ تایید و انتشار", callback_data=f"app_{message.chat.id}_{message.message_id}")
    btn_rej = types.InlineKeyboardButton("❌ رد کردن", callback_data=f"rej_{message.chat.id}_{message.message_id}")
    markup.add(btn_app, btn_rej)

    try:
        if message.text:
            # برای متن: اطلاعات را بالای متن می‌چسبانیم
            full_text = user_info + "📝 <b>متن پیام:</b>\n" + message.text
            bot.send_message(ADMIN_ID, full_text, reply_markup=markup, parse_mode='HTML')
        else:
            # برای فایل/عکس: اطلاعات را در کپشن می‌گذاریم
            bot.copy_message(
                chat_id=ADMIN_ID, 
                from_chat_id=message.chat.id, 
                message_id=message.message_id, 
                caption=user_info + (message.caption or ""), 
                reply_markup=markup, 
                parse_mode='HTML'
            )
        
        bot.reply_to(message, "✅ پیام شما دریافت شد و برای مدیریت ارسال گردید.")
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data.split('_')
    action, u_id, m_id = data[0], data[1], data[2]

    if action == "app":
        try:
            bot.copy_message(CHANNEL_ID, u_id, m_id)
            bot.answer_callback_query(call.id, "در کانال منتشر شد ✅")
            bot.edit_message_reply_markup(chat_id=ADMIN_ID, message_id=call.message.message_id, reply_markup=None)
            # نمایش وضعیت نهایی روی پیام
            if call.message.text:
                bot.edit_message_text(call.message.text + "\n\n✅ <b>منتشر شد</b>", chat_id=ADMIN_ID, message_id=call.message.message_id, parse_mode='HTML')
            else:
                bot.edit_message_caption(call.message.caption + "\n\n✅ <b>منتشر شد</b>", chat_id=ADMIN_ID, message_id=call.message.message_id, parse_mode='HTML')
        except:
            bot.answer_callback_query(call.id, "خطا در ارسال!")
            
    elif action == "rej":
        try:
            bot.delete_message(ADMIN_ID, call.message.message_id)
            bot.answer_callback_query(call.id, "پیام حذف شد.")
        except: pass

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    print("--- Robot is Starting ---")
    bot.infinity_polling(timeout=20, skip_pending=True)
