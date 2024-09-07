import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# ฟังก์ชันที่จะรันเมื่อผู้ใช้พิมพ์ /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('พร้อมรับใช้แล้วค่ะ!')

REPLACEMENT_URLS = {
    'x.com': 'fixupx.com',
    'twitter.com': 'fxtwitter.com',
    'pixiv.net': 'pixivview.net'  # ตัวอย่างลิงก์ที่แก้ไขสำหรับ pixiv
}

link_pattern = re.compile(r'(x|twitter|pixiv)\s*\.\s*(c\s*o\s*m|net|\(\s*c\s*o\s*m\s*\))', flags=re.IGNORECASE)

def replace_url(url, message):
    return message.replace(url, REPLACEMENT_URLS.get(url, url))

def detect_and_replace_links(message):
    # จับลิงก์ที่มีรูปแบบต่างๆ และแทนที่
    message = re.sub(link_pattern, r'\1.com', message)
    for url in REPLACEMENT_URLS.keys():
        message = replace_url(url, message)

    # จัดการลิงก์กรณีมีช่องว่างหลัง .com
    message = re.sub(r'(x.com|twitter.com|pixiv.net)\s+', r'\1', message)
    
    return message

def should_notify_owner(message):
    # เพิ่มเงื่อนไขการแจ้งเตือนเฉพาะกรณี
    return 'x.com' in message or 'twitter.com' in message or 'pixiv.net' in message

# ฟังก์ชันตรวจจับ @username และจัดการช่องว่าง
def fix_username_mentions(message):
    # แทนที่ช่องว่างหลัง @ ให้เป็นลิงก์ที่ถูกต้อง
    return re.sub(r'@\s*(\w+)', r'https://x.com/\1', message)

# ฟังก์ชันตรวจจับลิงก์และแก้ไข
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    try:
        # แก้ไขลิงก์ที่พบในข้อความ
        fixed_message = detect_and_replace_links(user_message)

        # ตรวจจับและแก้ไข @username
        fixed_message = fix_username_mentions(fixed_message)

        if 'x.com' in fixed_message or 'twitter.com' in fixed_message or 'pixiv.net' in fixed_message:
            await update.message.reply_text(f'เป้าหมายของคุณคือ: {fixed_message}')
            if should_notify_owner(fixed_message):
                await context.bot.send_message(chat_id=BOT_OWNER_ID, text=f'ตรวจพบลิงก์ในข้อความ: {fixed_message}')
        else:
            await update.message.reply_text('ด้วยความยินดีค่ะ')
            await context.bot.send_message(chat_id=BOT_OWNER_ID, text=f'{update.effective_user.first_name} : {user_message}')
    except Exception as e:
        await update.message.reply_text(f'เกิดข้อผิดพลาด: {str(e)}')

# ใส่ API Token ของคุณที่นี่
TOKEN = 'YOUR_REAL_BOT_API_TOKEN'
BOT_OWNER_ID = 'YOUR_BOT_OWNER_ID'


# สร้างแอปพลิเคชันบอท
app = ApplicationBuilder().token(TOKEN).build()

# เพิ่มคำสั่ง /start ให้บอท
app.add_handler(CommandHandler("start", start))

# ใช้ MessageHandler เพื่อตรวจจับข้อความที่ผู้ใช้ส่งมา
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# เริ่มรันบอท
app.run_polling()