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
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, "✅ <b>درود مدیریت!</b>\nربات آنلاین است و پیام‌های کاربران را برای شما می‌فرستد.", parse_mode='HTML')
    else:
        bot.reply_to(message, "سلام! پیام یا تصویر خود را بفرستید تا پس از تایید مدیریت، در کانال قرار بگیرد.")

@bot.message_handler(content_types=['text', 'photo'])
def handle_all_messages(message):
    # پیام‌های خود ادمین برای خودش فوروارد نمی‌شود
    if message.chat.id == ADMIN_ID:
        return

    user = message.from_user
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.datetime.now(tehran_tz)
    time_str = now.strftime('%H:%M:%S')
    
    chat_link = f"tg://user?id={user.id}"
    
    # استفاده از HTML برای جلوگیری از ارور کاراکترهای خاص
    user_info = (
        f"📩 <b>پیام جدید دریافت شد</b>\n"
        f"--------------------------\n"
        f"👤 <b>نام:</b> {user.first_name or '---'}\n"
        f"👤 <b>فامیل:</b> {user.last_name or 'ندارد'}\n"
        f"🆔 <b>آیدی:</b> <code>{user.id}</code>\n"
        f"🆔 <b>یوزرنیم:</b> @{user.username or 'ندارد'}\n"
        f"🌐 <b>زبان:</b> {user.language_code or '---'}\n"
        f"⏰ <b>ساعت:</b> {time_str}\n\n"
        f"🔗 <a href='{chat_link}'>ورود به پی‌وی کاربر</a>\n"
        f"--------------------------\n"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_app = types.InlineKeyboardButton("✅ تایید و ارسال", callback_data=f"app_{message.chat.id}_{message.message_id}")
    btn_rej = types.InlineKeyboardButton("❌ رد کردن و حذف", callback_data=f"rej_{message.chat.id}_{message.message_id}")
    markup.add(btn_app, btn_rej)

    try:
        if message.text:
            bot.send_message(ADMIN_ID, user_info + "📝 <b>متن پیام:</b>\n" + message.text, reply_markup=markup, parse_mode='HTML')
        elif message.photo:
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=user_info + "🖼 <b>توضیحات:</b>\n" + (message.caption or "بدون توضیح"), reply_markup=markup, parse_mode='HTML')
        
        bot.reply_to(message, "✅ پیام شما با موفقیت برای مدیریت ارسال شد.")
    except Exception as e:
        print(f"Send Error: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data.split('_')
    action, u_id, m_id = data[0], data[1], data[2]

    if action == "app":
        try:
            bot.copy_message(CHANNEL_ID, u_id, m_id)
            bot.answer_callback_query(call.id, "ارسال شد ✅")
            final_text = "✅ این پیام تایید و به کانال فرستاده شد."
            if call.message.photo:
                bot.edit_message_caption(final_text, chat_id=ADMIN_ID, message_id=call.message.message_id)
            else:
                bot.edit_message_text(final_text, chat_id=ADMIN_ID, message_id=call.message.message_id)
        except:
            bot.answer_callback_query(call.id, "خطا در ارسال!")
    elif action == "rej":
        try:
            bot.delete_message(ADMIN_ID, call.message.message_id)
            bot.answer_callback_query(call.id, "رد شد ❌")
        except: pass

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    
    # پاکسازی وب‌هوک برای رفع ارور تداخل
    bot.remove_webhook()
    time.sleep(2)
    
    print("--- Robot is Starting ---")
    # استفاده از infinity_polling برای پایداری در رندر
    bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
