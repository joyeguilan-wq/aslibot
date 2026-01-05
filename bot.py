import telebot
import time
from datetime import datetime
import pytz
import html
from threading import Thread
from flask import Flask

# تنظیمات سرور برای زنده نگه داشتن در کویب
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ۱. تنظیمات ربات (توکن خودت را بگذار)
API_TOKEN = '8356352784:AAGJcxp84RRXLTNWZyh_KXFTBREht7S4Kmw'
ADMIN_ID = 7189522324 

bot = telebot.TeleBot(API_TOKEN)
bot.remove_webhook()

user_db = {}

# تابع گزارش‌دهی با تمام جزئیات
def send_user_report(message):
    user = message.from_user
    tehran_tz = pytz.timezone('Asia/Tehran')
    time_now = datetime.now(tehran_tz).strftime("%H:%M:%S | %Y/%m/%d")
    
    # اطلاعات فرستنده
    f_name = html.escape(user.first_name) if user.first_name else "---"
    l_name = html.escape(user.last_name) if user.last_name else "---"
    u_name = html.escape(user.username) if user.username else "ندارد"
    u_lang = html.escape(user.language_code) if user.language_code else "نامشخص"
    user_link = f"https://t.me/{user.username}" if user.username else "ندارد"
    m_text = html.escape(message.caption if message.caption else (message.text if message.text else "بدون متن"))

    report = (
        f"📩 <b>پیام جدید دریافت شد</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 <b>نام:</b> {f_name}\n"
        f"👤 <b>نام خانوادگی:</b> {l_name}\n"
        f"🆔 <b>نام کاربری:</b> @{u_name}\n"
        f"🔢 <b>آیدی عددی:</b> <code>{user.id}</code>\n"
        f"🔗 <b>لینک چت:</b> {user_link}\n"
        f"🌍 <b>زبان تلگرام:</b> {u_lang}\n"
        f"⏰ <b>زمان:</b> {time_now}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📝 <b>متن/کپشن پیام:</b>\n{m_text}\n\n"
        f"👇 <i>برای پاسخ، روی پیام زیر ریپلای کنید.</i>"
    )
    
    bot.send_message(ADMIN_ID, report, parse_mode="HTML", disable_web_page_preview=True)

# دریافت انواع پیام (متن، عکس، فیلم و...)
@bot.message_handler(content_types=['text', 'photo', 'video', 'audio', 'voice', 'document', 'sticker'])
def handle_incoming_messages(message):
    if message.chat.id != ADMIN_ID:
        send_user_report(message)
        forwarded = bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        user_db[forwarded.message_id] = message.chat.id
        bot.reply_to(message, "ممنون:)\n\nعموجویی")

# پاسخ ادمین
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message)
def reply_to_user(message):
    fwd_msg_id = message.reply_to_message.message_id
    if fwd_msg_id in user_db:
        target_id = user_db[fwd_msg_id]
        try:
            bot.send_message(target_id, f"👤 <b>پاسخ مدیریت:</b>\n\n{html.escape(message.text)}", parse_mode="HTML")
            bot.send_message(ADMIN_ID, "✅ پاسخ شما ارسال شد.")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ خطا در ارسال: {e}")
    else:
        bot.send_message(ADMIN_ID, "⚠️ آیدی کاربر در حافظه نیست.")

# شروع همزمان سرور وب و ربات
if name == "main":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Bot and WebServer started...")
    bot.infinity_polling()
