import re
import random
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import os

load_dotenv()

# ตั้งค่า logging
# ตั้งค่า logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# สร้าง handler สำหรับแสดง log บนหน้าจอ
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# สร้าง handler สำหรับบันทึก log ลงไฟล์ด้วยการเข้ารหัส utf-8
file_handler = logging.FileHandler('bot.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ฟังก์ชันที่จะรันเมื่อผู้ใช้พิมพ์ /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('กองทหาร RABBIT พร้อมออกปฏิบัติการทุกเมื่อค่ะ')

# ฟังก์ชันซ่อมลิงก์
def fix_link(text):
    # ลบข้อความหน้าลิงก์ที่เริ่มต้นด้วย 'http' เช่น SChttps://...
    text = re.sub(r'\S*?(https?://\S+)', r'\1', text)
    # ลบช่องว่างระหว่าง protocol และ domain
    text = re.sub(r'(https?://)\s+', r'\1', text)

    # ตรวจสอบว่ามีลิงก์ fixupx.com หรือ fxtwitter.com แล้วหรือไม่
    if 'fixupx.com' in text or 'fxtwitter.com' in text:
        return text  # ไม่ต้องทำอะไรถ้าพบลิงก์ที่ถูกแก้แล้ว
    
    # ซ่อมลิงก์ x.com และ twitter.com
    text = re.sub(r'(x|twitter)\s*\.\s*com\s*/\s*', r'\1.com/', text, flags=re.IGNORECASE)
    text = re.sub(r'www\s*\.\s*twitter\s*\.\s*com\s*/\s*', r'www.twitter.com/', text, flags=re.IGNORECASE)
    text = re.sub(r'www\s*\.\s*x\s*\.\s*com\s*/\s*', r'www.x.com/', text, flags=re.IGNORECASE)
    
    # ซ่อมลิงก์ pixiv.net
    text = re.sub(r'pixiv\s*\.\s*net\s*/\s*', r'pixiv.net/', text, flags=re.IGNORECASE)
    text = re.sub(r'www\s*\.\s*pixiv\s*\.\s*net\s*/\s*', r'www.pixiv.net/', text, flags=re.IGNORECASE)
    
    # ลบข้อความหน้าลิงก์ pixiv
    text = re.sub(r'\S+?(https?://www\.pixiv\.net/)', r'\1', text)
    
    # จัดการกับ @username
    def handle_username(match):
        username = match.group(2).strip()
        if username.lower() == 'miyako_megubot':  # ชื่อบอทไม่แปลงลิงก์
            return f"@{username}"
        platform = random.choice(["x", "twitter"])
        return f"@{username} [{platform}.com/{username}]"
    
    text = re.sub(r'(?:(\w+)\s*@\s*|@\s*)(\w+)', handle_username, text)
    
    # แทนที่ลิงก์ x.com และ twitter.com ด้วย fixupx.com และ fxtwitter.com
    text = re.sub(r'(https?://)?(x\.com)', r'\1fixupx.com', text)
    text = re.sub(r'(https?://)?(twitter\.com)', r'\1fxtwitter.com', text)
    
    return text

# ฟังก์ชันตรวจจับและซ่อมลิงก์สำหรับคำสั่ง /fixlink
async def fixlink_command(update: Update, context: CallbackContext):
    # รับข้อความหลังจากคำสั่ง /fixlink
    if update.message and update.message.text:
        command_and_text = update.message.text.split(' ', 1)
        
        # ตรวจสอบว่ามีข้อความต่อจากคำสั่งหรือไม่
        if len(command_and_text) > 1:
            user_message = command_and_text[1]

            # ตรวจสอบและแก้ไขลิงก์
            fixed_message = fix_link(user_message)

            if fixed_message != user_message:
                await update.message.reply_text(f'ตรวจพบเป้าหมายแล้วค่ะ : {fixed_message}')
                logger.info(f'{update.effective_user.first_name} : {user_message}')
            else:
                await update.message.reply_text(f'ด้วยความยินดีค่ะ {update.effective_user.first_name}')
                logger.info(f'{update.effective_user.first_name} : {user_message}')
        else:
            await update.message.reply_text('กรุณาใส่ลิงก์ที่ต้องการซ่อมด้วยค่ะ')
    else:
        logger.warning('ข้อความว่างหรือไม่ได้รับการประมวลผล')

# ฟังก์ชันตรวจจับลิงก์ในแชทส่วนตัว (ไม่ต้องใช้คำสั่ง)
async def handle_private_message(update: Update, context: CallbackContext):
    if update.message and update.message.text:
        user_message = update.message.text
        fixed_message = fix_link(user_message)

        if fixed_message != user_message:
            await update.message.reply_text(f'ตรวจพบเป้าหมายแล้วค่ะ : {fixed_message}')
            logger.info(f'{update.effective_user.first_name} : {user_message}')
        else:
            await update.message.reply_text(f'ด้วยความยินดีค่ะ {update.effective_user.first_name}')
            logger.info(f'{update.effective_user.first_name} : {user_message}')
    else:
        await update.message.reply_text('ข้อความว่างหรือไม่ได้รับการประมวลผล')
        logger.warning('ข้อความว่างหรือไม่ได้รับการประมวลผล')

        # ฟังก์ชันจัดการข้อความจากกลุ่ม
async def handle_group_message(update: Update, context: CallbackContext):
    # ในกลุ่ม บอทจะไม่ตอบจนกว่าจะเรียกด้วยคำสั่ง
    if update.message and update.message.text.startswith(f'/fixlink@{BOT_NAME}'):
        await fixlink_command(update, context)
    else:
        return

BOT_NAME = os.getenv('BOT_NAME')
TOKEN = os.getenv('TOKEN')
BOT_OWNER_ID = os.getenv('BOT_OWNER_ID')

# สร้างแอปพลิเคชันบอท
app = ApplicationBuilder().token(TOKEN).build()

# เพิ่มคำสั่ง /start ให้บอท
app.add_handler(CommandHandler("start", start))

# กำหนด handler สำหรับการแชทส่วนตัว
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_private_message))

# กำหนด handler สำหรับการแชทในกลุ่ม
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message))

# ใช้ MessageHandler เพื่อตรวจจับข้อความที่ผู้ใช้ส่งมา
# app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# เริ่มรันบอท
app.run_polling()