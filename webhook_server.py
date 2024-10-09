import re
import random
import logging
import unicodedata
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import os
import asyncio

# โหลด environment variables
load_dotenv()

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,  # เปลี่ยนเป็น INFO เพื่อดู log เพิ่มเติม
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ดึงค่าคงที่จาก environment variables
TOKEN = os.getenv('TOKEN')
BOT_NAME = os.getenv('BOT_NAME')
BOT_OWNER_ID = os.getenv('BOT_OWNER_ID')

if not TOKEN:
    logger.error("TOKEN is not set. Please set the TOKEN environment variable.")
    exit(1)

# สร้าง FastAPI app
app = FastAPI()

# สร้าง Telegram bot application
application = ApplicationBuilder().token(TOKEN).build()

# ฟังก์ชันช่วยเหลือในการแปลงข้อความ
def full_to_half(text: str) -> str:
    return ''.join([unicodedata.normalize('NFKC', char) if unicodedata.east_asian_width(char) in ('W', 'F') else char for char in text])

def fixup_link(text: str) -> str:
    text = full_to_half(text)
    text = re.sub(r'\S*?(https?://\S+)', r'\1', text)
    text = re.sub(r'(https?://)\s+', r'\1', text)

    for domain in ['x', 'twitter', 'pixiv']:
        text = re.sub(fr'({domain})\s*\.\s*com\s*/\s*', fr'\1.com/', text, flags=re.IGNORECASE)
        text = re.sub(fr'www\s*\.\s*{domain}\s*\.\s*com\s*/\s*', fr'www.{domain}.com/', text, flags=re.IGNORECASE)

    text = re.sub(r"(https?://)?(www\.)?pixiv\.net/en/artworks/(\d+)", r"https://www.pixiv.net/en/artworks/\3", text, flags=re.IGNORECASE)

    if 'vxtwitter.com' not in text:
        text = re.sub(r'(https?://)?(x\.com|twitter\.com)', r'\1vxtwitter.com', text)

    text = re.sub(r'(x|twitter|@)(\s*[-:|\s]+\s*)(\w+)', handle_username_tx, text)
    text = re.sub(r'@(\w+)', handle_username, text)

    return text

def only_plain_text(text: str) -> str:
    text = re.sub(r'(artworks)\s*[-:\/|\s]+\s*(\d+)', handle_artwork, text)
    text = re.sub(r'(\w+)\s*/?\s*(status)\s*/?\s*(\d+)', handle_tx, text)
    return text

def clear_whitespace(text: str) -> str:
    return re.sub(r'\s+', '', text)

def handle_artwork(match) -> str:
    artworks_id = match.group(2).strip()
    return f"Pixiv: https://www.pixiv.net/en/artworks/{artworks_id}"

def handle_tx(match) -> str:
    username, status_id = match.group(1).strip(), match.group(3).strip()
    return f"@{username} https://x.com/{username}/status/{status_id}"

def handle_username_tx(match) -> str:
    username = match.group(3).strip()
    return f"@{username}" if username.lower() == BOT_NAME.lower() else f"@{username} [{random.choice(['x', 'twitter'])}.com/{username}]"

handle_username = handle_username_tx

# คำสั่ง /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('RABBIT 1 พร้อมออกปฏิบัติการทุกเมื่อค่ะ')

# คำสั่ง /link
async def link_command(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        user_message = update.message.text.split(' ', 1)[-1].strip()
        if user_message:
            cleaned_message = clear_whitespace(user_message)
            await update.message.reply_text(f'เป้าหมายใหม่ค่ะ! : {cleaned_message}')
            logger.info(f'/link {update.effective_user.first_name} : {cleaned_message}')
        else:
            await update.message.reply_text('ไม่ได้ใช้แบบนี้ค่ะ /link ตามลิงก์ที่ไม่สมบูรณ์ค่ะ')
    else:
        logger.warning('ข้อความว่างหรือไม่ได้รับการประมวลผล')

# คำสั่ง /fixup
async def fixup_command(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        user_message = update.message.text.split(' ', 1)[-1].strip()
        fixed_message = fixup_link(user_message)

        if fixed_message != user_message:
            await update.message.reply_text(f'ตรวจพบเป้าหมายแล้วค่ะ : {fixed_message}')
            logger.info(f'{update.effective_user.first_name} : {fixed_message}')
        else:
            fixed_message = only_plain_text(user_message)
            if fixed_message != user_message:
                await update.message.reply_text(f'ตรวจพบเป้าหมายแล้วค่ะ : {fixed_message}')
                logger.warning(f'รองด่านสุดท้าย {update.effective_user.first_name} : {user_message}')
            else:
                half_message = full_to_half(user_message)
                fixed_message = clear_whitespace(half_message)
                if fixed_message != user_message:
                    await update.message.reply_text(f'แบบนี้รึปล่าวคะ? : {fixed_message}')
                    logger.warning(f'ด่านสุดท้าย {update.effective_user.first_name} : {user_message}')
                else:
                    await update.message.reply_text(f'ขอโทษค่ะแก้ไขไม่ได้จะบันทึกไว้นะคะ {update.effective_user.first_name}')
                    logger.warning(f'แก้ไขให้ไม่ได้ {update.effective_user.first_name} : {user_message}')
    else:
        await update.message.reply_text('กรุณาใส่ลิงก์ที่ต้องการซ่อมด้วยค่ะ')

# การจัดการข้อความส่วนตัว
async def handle_private_message(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        await fixup_command(update, context)
    else:
        await update.message.reply_text('ข้อความว่างหรือไม่ได้รับการประมวลผล')
        logger.warning('ข้อความว่างหรือไม่ได้รับการประมวลผล')

# การจัดการข้อความกลุ่ม
async def handle_group_message(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        user_message = update.message.text
        if user_message.startswith(('/fixup', f'/fixup@{BOT_NAME}')):
            await fixup_command(update, context)
        elif user_message.startswith(('/link', f'/link@{BOT_NAME}')):
            await link_command(update, context)

# คำสั่ง /bug
async def report_bug_command(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        user_message = update.message.text.split(' ', 1)[-1].strip()
        if user_message:
            await update.message.reply_text(f'รับทราบแล้วค่ะจะทำเรื่องบันทึกไว้ให้นะคะ {update.effective_user.first_name}')
            logger.warning(f'รายงานบัค :{update.effective_user.first_name} : {user_message}')
        else:
            await update.message.reply_text('สามารถพิมพ์ รายงานโดยการ กด /bug ตามด้วยข้อความได้เลยค่ะ')

# คำสั่ง /privacy
async def privacy_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('ระบบจะทำการเก็บข้อมูลการใช้งานไปวิเคราะห์และปรับปรุงให้ดียิ่งขึ้นค่ะ')

# เพิ่ม handler สำหรับคำสั่งต่าง ๆ
commands = [
    ("start", start, "เริ่มใช้งาน"),
    ("link", link_command, "ลบช่องว่างระหว่างลิงก์"),
    ("fixup", fixup_command, "แก้ไขลิงก์ @x.com,@twitter.com,pixiv.net"),
    ("bug", report_bug_command, "รายงานบัค"),
    ("privacy", privacy_command, "เกี่ยวกับนโยบายความเป็นส่วนตัว")
]

for command, handler, description in commands:
    application.add_handler(CommandHandler(command, handler))

# เพิ่ม handler สำหรับข้อความ
application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_private_message))
application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message))

# Route สำหรับตรวจสอบเซิร์ฟเวอร์
@app.get("/")
async def home():
    return {"message": "Hello World"}

# Route สำหรับ Webhook
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

# Startup event เพื่อเริ่มต้นบอท
@app.on_event("startup")
async def startup_event():
    await application.initialize()
    await application.start()
    logger.info("Telegram bot started.")

# Shutdown event เพื่อหยุดบอท
@app.on_event("shutdown")
async def shutdown_event():
    await application.stop()
    logger.info("Telegram bot stopped.")

# รัน FastAPI ผ่าน Uvicorn
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("webhook_server:app", host='0.0.0.0', port=5000, log_level="info")