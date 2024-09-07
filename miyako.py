import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# ฟังก์ชันที่จะรันเมื่อผู้ใช้พิมพ์ /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('พร้อมรับใช้แล้วค่ะ!')

# ฟังก์ชันตรวจจับลิงก์และแก้ไข
async def handle_message(update: Update, context: CallbackContext):
    # รับข้อความจากผู้ใช้
    user_message = update.message.text
    
    # แก้ไขลิงก์ที่มีช่องว่างระหว่างตัวอักษร c, o, m และวงเล็บ
    fixed_message = re.sub(r'x\s*\.\s*\(\s*c\s*o\s*m\s*\)', 'x.com', user_message, flags=re.IGNORECASE)
    fixed_message = re.sub(r'x\s*\.\s*c\s*\s*o\s*\s*m', 'x.com', fixed_message, flags=re.IGNORECASE)
    fixed_message = re.sub(r'twitter\s*\.\s*\(\s*c\s*o\s*m\s*\)', 'twitter.com', fixed_message, flags=re.IGNORECASE)
    fixed_message = re.sub(r'twitter\s*\.\s*c\s*\s*o\s*\s*m', 'twitter.com', fixed_message, flags=re.IGNORECASE)

    # แก้ไขลิงก์ที่มีช่องว่างระหว่าง . และ com พร้อมกับ path
    fixed_message = re.sub(r'https://\s*x\s*\.\s*\(\s*c\s*o\s*m\s*\)', 'https://x.com', fixed_message, flags=re.IGNORECASE)
    fixed_message = re.sub(r'https://\s*x\s*\.\s*c\s*\s*o\s*\s*m', 'https://x.com', fixed_message, flags=re.IGNORECASE)
    fixed_message = re.sub(r'https://\s*twitter\s*\.\s*\(\s*c\s*o\s*m\s*\)', 'https://twitter.com', fixed_message, flags=re.IGNORECASE)
    fixed_message = re.sub(r'https://\s*twitter\s*\.\s*c\s*\s*o\s*\s*m', 'https://twitter.com', fixed_message, flags=re.IGNORECASE)
    
    # แก้ไขลิงก์ที่มีช่องว่างหลัง .com
    fixed_message = re.sub(r'(x.com)\s+', r'\1', fixed_message)
    fixed_message = re.sub(r'(twitter.com)\s+', r'\1', fixed_message)

    # แก้ไขลิงก์ที่ไม่มี https://
    fixed_message = re.sub(r'x\s*\.\s*\(\s*c\s*o\s*m\s*\)', 'x.com', fixed_message, flags=re.IGNORECASE)
    fixed_message = re.sub(r'x\s*\.\s*c\s*\s*o\s*\s*m', 'x.com', fixed_message, flags=re.IGNORECASE)
    fixed_message = re.sub(r'twitter\s*\.\s*\(\s*c\s*o\s*m\s*\)', 'twitter.com', fixed_message, flags=re.IGNORECASE)
    fixed_message = re.sub(r'twitter\s*\.\s*c\s*\s*o\s*\s*m', 'twitter.com', fixed_message, flags=re.IGNORECASE)

    # ตรวจสอบว่ามี 'x.com' หรือ 'twitter.com' ในข้อความหรือไม่
    if 'x.com' in fixed_message:
        # แทนที่ลิงก์ x.com ด้วย fixupx.com
        fixed_message = fixed_message.replace('x.com', 'fixupx.com')
        await update.message.reply_text(f'เป้าหมายของคุณคือ: {fixed_message}')
        # ส่งข้อความไปยังผู้สร้าง
        await context.bot.send_message(chat_id=BOT_OWNER_ID, text=f'ตรวจพบลิงก์ x.com ในข้อความ: {fixed_message}')
    elif 'twitter.com' in fixed_message:
        # แทนที่ลิงก์ twitter.com ด้วย fxtwitter.com
        fixed_message = fixed_message.replace('twitter.com', 'fxtwitter.com')
        await update.message.reply_text(f'เป้าหมายของคุณคือ: {fixed_message}')
        # ส่งข้อความไปยังผู้สร้าง
        await context.bot.send_message(chat_id=BOT_OWNER_ID, text=f'ตรวจพบลิงก์ twitter.com ในข้อความ: {fixed_message}')
    elif re.search(r'@(\w+)', fixed_message):
        # แปลงข้อความจาก @{...} เป็น x.com/...
        fixed_message = re.sub(r'@(\w+)', r'https://x.com/\1', fixed_message)
        await update.message.reply_text(f'เป้าหมายของคุณคือ : {fixed_message}')
        # ส่งข้อความไปยังผู้สร้าง
        await context.bot.send_message(chat_id=BOT_OWNER_ID, text=f'ตรวจพบ @username ในข้อความ: {fixed_message}')
    else:
        # ตอบกลับเมื่อไม่พบลิงก์หรือ @
        await update.message.reply_text('ด้วยความยินดีค่ะ')
        await context.bot.send_message(chat_id=BOT_OWNER_ID, text=f'{update.effective_user.first_name} : {user_message}')

# ใส่ API Token ของคุณที่นี่
TOKEN = 'YOUR_REAL_BOT_API_TOKEN'
# ใส่ ID ของผู้สร้างบอทที่นี่
BOT_OWNER_ID = 'YOUR_BOT_OWNER_ID'

# สร้างแอปพลิเคชันบอท
app = ApplicationBuilder().token(TOKEN).build()

# เพิ่มคำสั่ง /start ให้บอท
app.add_handler(CommandHandler("start", start))

# ใช้ MessageHandler เพื่อตรวจจับข้อความที่ผู้ใช้ส่งมา
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# เริ่มรันบอท
app.run_polling()