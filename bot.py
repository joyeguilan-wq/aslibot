import telebot
import time
from datetime import datetime
import pytz
import html

# ۱. توکن و آیدی خودت را اینجا چک کن
API_TOKEN = '8356352784:AAGJcxp84RRXLTNWZyh_KXFTBREht7S4Kmw'
ADMIN_ID = 7189522324

bot = telebot.TeleBot(API_TOKEN)
bot.remove_webhook()

user_db = {}

# تابعی برای ساخت گزارش کامل (شامل زبان که خودت اضافه کردی)
def send_user_report(message):
    user = message.from_user
    tehran_tz = pytz.timezone('Asia/Tehran')
    time_now = datetime.now(tehran_tz).strftime("%H:%M:%S | %Y/%m/%d")
    user_link = f"https://t.me/{user.username}" if user.username else "ندارد"

    # ایمن‌سازی مقادیر برای جلوگیری از ارور 400
    f_name = html.escape(user.first_name) if user.first_name else "---"
    l_name = html.escape(user.last_name) if user.last_name else "---"
    u_name = html.escape(user.username) if user.username else "ندارد"
    u_lang = html.escape(user.language_code) if user.language_code else "نامشخص"
    m_text = html.escape(message.caption if message.caption else (message.text if message.text else "بدون متن"))

    report = (
        f"📩 <b>اطلاعات فرستنده:</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 <b>نام:</b> {f_name}\n"
        f"👤 <b>فامیل:</b> {l_name}\n"
        f"🆔 <b>یوزرنیم:</b> @{u_name}\n"
        f"🔢 <b>آیدی عددی:</b> <code>{user.id}</code>\n"
        f"🔗 <b>لینک چت:</b> {user_link}\n"
        f"🌍 <b>زبان تلگرام:</b> {u_lang}\n"
        f"⏰ <b>زمان:</b> {time_now}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📝 <b>متن/کپشن:</b>\n{m_text}\n\n"
        f"👈 <i>برای پاسخ، روی فایل/پیام زیر ریپلای کنید.</i>"
    )
    bot.send_message(ADMIN_ID, report, parse_mode="HTML", disable_web_page_preview=True)

# دریافت انواع پیام (متن، عکس، فیلم، فایل و...)
@bot.message_handler(content_types=['text', 'photo', 'video', 'audio', 'voice', 'document', 'sticker'])
def handle_incoming_messages(message):
    if message.chat.id != ADMIN_ID:
        # ارسال شناسنامه کاربر
        send_user_report(message)

        # فوروارد پیام اصلی (برای دیدن فایل و امکان ریپلای)
        forwarded = bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

        # ذخیره برای سیستم ریپلای
        user_db[forwarded.message_id] = message.chat.id

        # پاسخ به کاربر
        bot.reply_to(message, "ممنون:)\n\nعموجویی")

# سیستم ریپلای ادمین
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
        bot.send_message(ADMIN_ID, "⚠️ کاربر پیدا نشد (احتمالا ربات ریست شده یا روی پیام اشتباهی ریپلای کردید).")

print("Bot is Running...")
bot.infinity_polling()
