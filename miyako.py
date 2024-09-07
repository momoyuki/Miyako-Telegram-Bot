import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# ฟังก์ชันที่จะรันเมื่อผู้ใช้พิมพ์ /start
async def start(update: Update, context):
    await update.message.reply_text('พร้อมรับใช้แล้วค่ะ!')

# ฟังก์ชันตรวจจับลิงก์และแก้ไข
async def handle_message(update: Update, context):
    # รับข้อความจากผู้ใช้
    user_message = update.message.text

    # ตรวจสอบว่ามี 'x.com' หรือ 'twitter.com' ในข้อความหรือไม่
    if 'x.com' in user_message:
        # แทนที่ลิงก์ x.com ด้วย fixupx.com
        fixed_message = user_message.replace('x.com', 'fixupx.com')
        await update.message.reply_text(f'ลิงก์ใหม่ของคุณคือ: {fixed_message}')
    elif 'twitter.com' in user_message:
        # แทนที่ลิงก์ twitter.com ด้วย fxtwitter.com
        fixed_message = user_message.replace('twitter.com', 'fxtwitter.com')
        await update.message.reply_text(f'ลิงก์ใหม่ของคุณคือ: {fixed_message}')
    elif re.search(r'@(\w+)', user_message):
        # แปลงข้อความจาก @{...} เป็น x.com/...
        fixed_message = re.sub(r'@(\w+)', r'https://x.com/\1', user_message)
        await update.message.reply_text(f'เป้าหมายของคุณคือ : {fixed_message}')
    
    else:
        await update.message.reply_text('ไม่มีลิงก์ที่ต้องแก้ไขในข้อความของคุณ')

# ใส่ API Token ของคุณที่นี่
TOKEN = 'YOUR_REAL_BOT_API_TOKEN'

# สร้างแอปพลิเคชันบอท
app = ApplicationBuilder().token(TOKEN).build()

# เพิ่มคำสั่ง /start ให้บอท
app.add_handler(CommandHandler("start", start))

# ใช้ MessageHandler เพื่อตรวจจับข้อความที่ผู้ใช้ส่งมา
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# เริ่มรันบอท
app.run_polling()