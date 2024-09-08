import re
import random
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import os

load_dotenv()

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
    await update.message.reply_text('RABBIT 1 พร้อมออกปฏิบัติการทุกเมื่อค่ะ')

def clear_whitespace(text):
    return re.sub(r'\s+', '', text)

# ฟังก์ชันซ่อมลิงก์
def fixup_link(text):
    # ลบข้อความหน้าลิงก์ที่เริ่มต้นด้วย 'http' เช่น SChttps://...
    text = re.sub(r'\S*?(https?://\S+)', r'\1', text)
    # ลบช่องว่างระหว่าง protocol และ domain
    text = re.sub(r'(https?://)\s+', r'\1', text)
    text = re.sub(r'(https?://)\s*([a-zA-Z0-9.-]+)\s*\.\s*([a-zA-Z]{2,})', r'\1\2.\3', text)

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
    text = re.sub(r'(artworks)\s*[-:/|\s]+\s*(\d+)',handle_artwork,text)

    # ซ่อมลิงก์ที่เกี่ยวข้องกับ artworks
    text = re.sub(r"(https?://)?(www\.)?pixiv\.net/en/artworks/(\d+)", r"https://www.pixiv.net/en/artworks/\3", text, flags=re.IGNORECASE)

    text = re.sub(r'(\w+)\s*/?\s*(status)\s*/?\s*(\d+)',handle_tx,text)

    # ทำเป็นอีกฟังก์ชั่น
    # แทนที่ลิงก์ x.com และ twitter.com ด้วย fixupx.com และ fxtwitter.com
    text = re.sub(r'(https?://)?(x\.com)', r'\1fixupx.com', text)
    text = re.sub(r'(https?://)?(twitter\.com)', r'\1fxtwitter.com', text)
    # จัดการกับ @username แก้โดยดัก @ถ้าเจอ แทนที่ด้วยลิงก์
    
    text = re.sub(r'@(\w+)', handle_username, text)
    text = re.sub(r'(x|twitter|@)(\s*[-:|\s]+\s*)(\w+)', handle_username_tx, text)

   
    # text = re.sub(r'(?:@|X|Twitter)\s*:\s*(\w+)', handle_username, text, flags=re.IGNORECASE)

    return text

def handle_artwork(match):
    artworks_id = match.group(2).strip()
    return f"https://www.pixiv.net/en/artworks/{artworks_id}"

def handle_tx(match):
    username = match.group(1).strip()
    status_id = match.group(3).strip()
    return f"@{username} https://x.com/{username}/status/{status_id}"

 # จัดการกับ @username
def handle_username_tx(match):
    username = match.group(3).strip()
    if username.lower() == BOT_NAME:
        return f"@{username}"
    platform = random.choice(["x", "twitter"])
    return f"@{username} [{platform}.com/{username}]"

def handle_username(match):
    username = match.group(1).strip()
    if username.lower() == BOT_NAME:
        return f"@{username}"
    platform = random.choice(["x", "twitter"])
    return f"@{username} [{platform}.com/{username}]"

###########################คำสั่ง###########################

async def link_command(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text[len('/link '):].strip()
    if user_message:
        cleaned_message = clear_whitespace(user_message)
        await update.message.reply_text(f'เป้าหมายใหม่ค่ะ! : {cleaned_message}')
        logger.warning(f'/link {update.effective_user.first_name} : {cleaned_message}')
    else:
        await update.message.reply_text('ไม่ได้ใช้แบบนี้ค่ะ /link ตามลิงก์ที่ไม่สมบูรณ์ค่ะ')

async def fixup_command(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        command_and_text = update.message.text.split(' ', 1)
        if len(command_and_text) > 1:
            user_message = command_and_text[1]
            fixed_message = fixup_link(user_message)
            if fixed_message != user_message:
                await update.message.reply_text(f'ตรวจพบเป้าหมายแล้วค่ะ : {fixed_message}')
                logger.info(f'{update.effective_user.first_name} : {fixed_message}')
            else:
                await update.message.reply_text(f'ขอโทษค่ะแก้ไขไม่ได้จะบันทึกไว้นะคะ {update.effective_user.first_name}')
                logger.warning(f'{update.effective_user.first_name} : {user_message}')
        else:
            await update.message.reply_text('กรุณาใส่ลิงก์ที่ต้องการซ่อมด้วยค่ะ')
    else:
        logger.warning('ข้อความว่างหรือไม่ได้รับการประมวลผล')

################################################################################################

async def handle_private_message(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        user_message = update.message.text
        fixed_message = fixup_link(user_message)
        if fixed_message != user_message:
            await update.message.reply_text(f'ตรวจพบเป้าหมายแล้วค่ะ : {fixed_message}')
            logger.info(f'{update.effective_user.first_name} : {user_message}')
        else:
            await update.message.reply_text(f'ขอโทษค่ะแก้ไขไม่ได้จะบันทึกไว้นะคะ {update.effective_user.first_name}')
            logger.warning(f'{update.effective_user.first_name} : {user_message}')
    else:
        await update.message.reply_text('ข้อความว่างหรือไม่ได้รับการประมวลผล')
        logger.warning('ข้อความว่างหรือไม่ได้รับการประมวลผล')

async def handle_group_message(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        if update.message.text.startswith(f'/fixup@{BOT_NAME}'):
            await fixup_command(update, context)
        elif update.message.text.startswith(f'/link@{BOT_NAME}'):
            await link_command(update, context)

################################################################################################


TOKEN = os.getenv('TOKEN')
BOT_NAME = os.getenv('BOT_NAME')
BOT_OWNER_ID = os.getenv('BOT_OWNER_ID')

# สร้างแอปพลิเคชันบอท
app = ApplicationBuilder().token(TOKEN).build()

# เพิ่มคำสั่ง /start ให้บอท
app.add_handler(CommandHandler("start", start))

# เพิ่มคำสั่ง /link ให้บอท
app.add_handler(CommandHandler("link", link_command))

# เพิ่มคำสั่ง /fixup ให้บอท
app.add_handler(CommandHandler("fixup", fixup_command))


# start - เริ่มใช้งาน
# link - ลบช่องว่างระหว่างลิงก์
# fixup - แก้ไขลิงก์ @x.com,@twitter.com,pixiv.net  

# กำหนด handler สำหรับการแชทส่วนตัว
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_private_message))
# กำหนด handler สำหรับการแชทในกลุ่ม
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message))

# เริ่มรันบอท
app.run_polling()