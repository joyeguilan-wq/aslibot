import telebot
from telebot import types
from flask import Flask
from threading import Thread
import os
import datetime

# --- تنظیمات اصلی (دریافت از Environment برای امنیت و دقت بالا) ---
API_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 7189522324  # آیدی عددی خودت را اینجا بگذار
CHANNEL_ID = -1003630209623  # آیدی کانال را اینجا بگذار

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- دستور استارت ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if str(message.chat.id) == str(ADMIN_ID):
        bot.reply_to(message, "سلام ! در حال ارتباط ناشناس با عموجویی هستی. ✅")
    else:
        bot.reply_to(message, "سلام! پیام خود را بفرستید تا پس از تایید عموجویی در کانال قرار بگیرد.")

# --- مدیریت پیام‌های ورودی (متن و عکس) ---
@bot.message_handler(content_types=['text', 'photo'])
def handle_all_messages(message):
    # پیام‌های خود ادمین رو نادیده بگیر تا لوپ نشه
    if str(message.chat.id) == str(ADMIN_ID):
        return

    user = message.from_user
    date = datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
    
    # ساخت لینک مستقیم به پی‌وی کاربر
    chat_link = f"tg://user?id={user.id}"
    
    user_info = (
        f"📩 *پیام جدید دریافت شد:*\n\n"
        f"👤 نام: {user.first_name}\n"
        f"👤 فامیل: {user.last_name or 'ندارد'}\n"
        f"🆔 آیدی: `{user.id}`\n"
        f"username: @{user.username or 'ندارد'}\n"
        f"🌐 زبان: {user.language_code}\n"
        f"⏰ زمان: {date}\n\n"
        f"🔗 [لینک چت مستقیم با کاربر]({chat_link})\n"
        f"----------------------\n"
    )

    # ایجاد دکمه‌های تایید و رد
    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton("✅ تایید و ارسال به کانال", callback_data=f"app_{message.chat.id}_{message.message_id}")
    reject_btn = types.InlineKeyboardButton("❌ رد کردن", callback_data=f"rej_{message.chat.id}_{message.message_id}")
    markup.add(approve_btn, reject_btn)

    try:
        if message.text:
            bot.send_message(ADMIN_ID, user_info + "متن پیام:\n" + message.text, reply_markup=markup, parse_mode='Markdown')
        elif message.photo:
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=user_info + "توضیحات عکس:\n" + (message.caption or "ندارد"), reply_markup=markup, parse_mode='Markdown')
        
        bot.reply_to(message, "ممنون؛ از طرف عمو جویی .")
    except Exception as e:
        print(f"Error sending to admin: {e}")

# --- مدیریت دکمه‌های شیشه‌ای ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data.split('_')
    action = data[0]
    user_chat_id = data[1]
    msg_id = data[2]

    if action == "app":
        try:
            # ارسال پیام به کانال
            bot.copy_message(CHANNEL_ID, user_chat_id, msg_id)
            bot.answer_callback_query(call.id, "به کانال ارسال شد ✅")
            
            # تغییر وضعیت پیام در پی‌وی ادمین
            success_text = "این پیام تایید و به کانال ارسال شد. ✅"
            if call.message.photo:
                bot.edit_message_caption(success_text, chat_id=ADMIN_ID, message_id=call.message.message_id)
            else:
                bot.edit_message_text(success_text, chat_id=ADMIN_ID, message_id=call.message.message_id)
        except Exception as e:
            bot.answer_callback_query(call.id, "خطا! آیدی کانال اشتباه است یا ربات ادمین نیست.")
            print(f"Channel Error: {e}")

    elif action == "rej":
        try:
            bot.delete_message(ADMIN_ID, call.message.message_id)
            bot.answer_callback_query(call.id, "پیام رد و حذف شد ❌")
        except:
            bot.answer_callback_query(call.id, "خطا در حذف پیام!")

# --- اجرای همزمان وب‌سرور و ربات ---
if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Bot is Starting...")
    # استفاده از پولینگ معمولی برای پایداری بیشتر در رندر
    bot.polling(none_stop=True, interval=0, timeout=20)
