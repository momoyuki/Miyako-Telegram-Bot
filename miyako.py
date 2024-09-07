import re
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# ฟังก์ชันที่จะรันเมื่อผู้ใช้พิมพ์ /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('กองทหาร RABBIT พร้อมออกปฏิบัติการทุกเมื่อค่ะ')

# ฟังก์ชันซ่อมลิงก์
def fix_link(text):
    # ลบช่องว่างระหว่าง protocol และ domain
    text = re.sub(r'(https?://)\s+', r'\1', text)
    
    # ซ่อมลิงก์ x.com และ twitter.com
    text = re.sub(r'(x|twitter)\s*\.\s*com\s*/\s*', r'\1.com/', text, flags=re.IGNORECASE)
    
    # ซ่อมลิงก์ pixiv.net
    text = re.sub(r'pixiv\s*\.\s*net\s*/\s*', r'pixiv.net/', text, flags=re.IGNORECASE)
    text = re.sub(r'www\s*\.\s*pixiv\s*\.\s*net\s*/\s*', r'www.pixiv.net/', text, flags=re.IGNORECASE)
    
    # ลบข้อความหน้าลิงก์ pixiv
    text = re.sub(r'\S+?(https?://www\.pixiv\.net/)', r'\1', text)
    
    # จัดการกับ @username
    def handle_username(match):
        username = match.group(2).strip()
        platform = random.choice(["x", "twitter"])
        return f"@{username} [{platform}.com/{username}]"
    
    text = re.sub(r'(?:(\w+)\s*@\s*|@\s*)(\w+)', handle_username, text)
    
    # แทนที่ลิงก์ x.com และ twitter.com ด้วย fixupx.com และ fxtwitter.com
    text = re.sub(r'(https?://)?(x\.com)', r'\1fixupx.com', text)
    text = re.sub(r'(https?://)?(twitter\.com)', r'\1fxtwitter.com', text)
    
    return text

# ฟังก์ชันตรวจจับลิงก์และแก้ไข
async def handle_message(update: Update, context: CallbackContext):
    # รับข้อความจากผู้ใช้
    user_message = update.message.text
    
    # ซ่อมลิงก์
    fixed_message = fix_link(user_message)
    
    # ตรวจสอบว่ามีการเปลี่ยนแปลงหรือไม่
    if fixed_message != user_message:
        await update.message.reply_text(f'ตรวจพบเป้าหมายแล้วค่ะ : {fixed_message}')
        await context.bot.send_message(chat_id=BOT_OWNER_ID, text=f'ตรวจพบขึ้นเรือ: {fixed_message}')
    else:
        # ตอบกลับเมื่อไม่พบลิงก์ที่ต้องซ่อม
        await update.message.reply_text(f'ด้วยความยินดีค่ะ {update.effective_user.first_name}')
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