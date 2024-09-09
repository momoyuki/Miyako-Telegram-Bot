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


def fixup_link(text):
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
    
    

    # ซ่อมลิงก์ที่เกี่ยวข้องกับ artworks
    text = re.sub(r"(https?://)?(www\.)?pixiv\.net/en/artworks/(\d+)", r"https://www.pixiv.net/en/artworks/\3", text, flags=re.IGNORECASE)

    # แทนที่ลิงก์ x.com และ twitter.com ด้วย fixupx.com และ fxtwitter.com
    text = re.sub(r'(https?://)?(x\.com)', r'\1fixupx.com', text)
    text = re.sub(r'(https?://)?(twitter\.com)', r'\1fxtwitter.com', text)

    # จัดการกับ @username
    text = re.sub(r'(x|twitter|@)(\s*[-:|\s]+\s*)(\w+)', handle_username_tx, text)
    text = re.sub(r'@(\w+)', handle_username, text)
    
    return text

def only_plain_text(text):
    #TODO แก้บัค กรณี หลุดเซ็ตอื่น
    text = re.sub(r'(artworks)\s*[-:/|\s]+\s*(\d+)', handle_artwork, text) 
    text = re.sub(r'(\w+)\s*/?\s*(status)\s*/?\s*(\d+)', handle_tx, text)
    return text

# ฟังก์ชันลบช่องว่าง
def clear_whitespace(text):
    return re.sub(r'\s+', '', text)

# จัดการกับ Pixiv artworks #TODO แก้บัค กรณี หลุดเซ็ตอื่น
def handle_artwork(match):
    artworks_id = match.group(2).strip()
    return f"https://www.pixiv.net/en/artworks/{artworks_id}"

# จัดการกับ Twitter และ X status #TODO แก้บัค กรณี หลุดเซ็ตอื่น
def handle_tx(match):
    username = match.group(1).strip()
    status_id = match.group(3).strip()
    return f"@{username} https://x.com/{username}/status/{status_id}"

# จัดการกับ @username บนแพลตฟอร์ม Twitter หรือ X
def handle_username_tx(match):
    username = match.group(3).strip()
    if username.lower() == BOT_NAME:
        return f"@{username}"
    platform = random.choice(["x", "twitter"])
    return f"@{username} [{platform}.com/{username}]"

# จัดการกับ @username ทั่วไป
def handle_username(match):
    username = match.group(1).strip()
    if username.lower() == BOT_NAME:
        return f"@{username}"
    platform = random.choice(["x", "twitter"])
    return f"@{username} [{platform}.com/{username}]"

# ฟังก์ชันที่จะรันเมื่อผู้ใช้พิมพ์ /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('RABBIT 1 พร้อมออกปฏิบัติการทุกเมื่อค่ะ')

async def link_command(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        command_and_text = update.message.text.split(' ', 1)
        if len(command_and_text) > 1:
            user_message = command_and_text[1].strip()  # ดึงข้อความต่อจากคำสั่ง /link
            if user_message:
                cleaned_message = clear_whitespace(user_message)
                await update.message.reply_text(f'เป้าหมายใหม่ค่ะ! : {cleaned_message}')
                logger.info(f'/link {update.effective_user.first_name} : {cleaned_message}')
            else:
                await update.message.reply_text('ไม่ได้ใช้แบบนี้ค่ะ /link ตามลิงก์ที่ไม่สมบูรณ์ค่ะ')
        else:
            await update.message.reply_text('กรุณาใส่ลิงก์ที่ต้องการซ่อมด้วยค่ะ')
    else:
        logger.warning('ข้อความว่างหรือไม่ได้รับการประมวลผล')

async def fixup_command(update: Update, context: CallbackContext) -> None:
    if update.message and update.message.text:
        command_and_text = update.message.text.split(' ', 1)
        if len(command_and_text) > 1:
            user_message = command_and_text[1].strip()
            fixed_message = fixup_link(user_message)
            if fixed_message != user_message:
                await update.message.reply_text(f'ตรวจพบเป้าหมายแล้วค่ะ : {fixed_message}')
                logger.info(f'{update.effective_user.first_name} : {fixed_message}')
            else:
                #TODO
                fixed_message = only_plain_text(user_message)
                if fixed_message != user_message:
                    await update.message.reply_text(f'ตรวจพบเป้าหมายแล้วค่ะ : {fixed_message}')
                    logger.warning(f'ด่านสุดท้าย {update.effective_user.first_name} : {user_message}')
                else:   
                #TODO
                    await update.message.reply_text(f'ขอโทษค่ะแก้ไขไม่ได้จะบันทึกไว้นะคะ {update.effective_user.first_name}')
                    logger.warning(f'{update.effective_user.first_name} : {user_message}')
        else:
            await update.message.reply_text('กรุณาใส่ลิงก์ที่ต้องการซ่อมด้วยค่ะ')
    else:
        logger.warning('ข้อความว่างหรือไม่ได้รับการประมวลผล')

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
        user_message = update.message.text

        # ตรวจสอบทั้งกรณีที่มีชื่อบอทและไม่มีชื่อบอท
        if user_message.startswith(f'/fixup@{BOT_NAME}') or user_message.startswith('/fixup'):
            await fixup_command(update, context)
        elif user_message.startswith(f'/link@{BOT_NAME}') or user_message.startswith('/link'):
            await link_command(update, context)
        # else:
        #     # ข้อความที่ไม่ได้ใช้คำสั่ง
        #     logger.info(f'{update.effective_user.first_name} ส่งข้อความที่ไม่ใช่คำสั่ง: {user_message}')

async def repot_bug_command(update: Update, context: CallbackContext):
    if update.message and update.message.text:
        command_and_text = update.message.text.split(' ', 1)
        if len(command_and_text) > 1:
            user_message = command_and_text[1].strip()
            await update.message.reply_text(f'รับทราบแล้วค่ะจะทำเรื่องบันทึกไว้ให้นะคะ {update.effective_user.first_name}')
            logger.warning(f'รายงานบัค :{update.effective_user.first_name} : {user_message}')
        else:
         await update.message.reply_text('สามารถพิมพ์ รายงานโดยการ กด /bug ตามด้วยข้อความได้เลยค่ะ')

async def privacy_command(update: Update, context: CallbackContext):
    await update.message.reply_text('ระบบจะทำการเก็บข้อมูลการใช้งานไปวิเคราะห์และปรับปรุงให้ดียิ่งขึ้นค่ะ')


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

app.add_handler(CommandHandler("bug", repot_bug_command))

app.add_handler(CommandHandler("privacy", privacy_command))

# start - เริ่มใช้งาน
# link - ลบช่องว่างระหว่างลิงก์
# fixup - แก้ไขลิงก์ @x.com,@twitter.com,pixiv.net 
# bug - รายงานบัค
# privacy - เกี่ยวกับนโยบายความเป็นส่วนตัว 

# กำหนด handler สำหรับการแชทส่วนตัว
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_private_message))
# กำหนด handler สำหรับการแชทในกลุ่ม
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message))

# เริ่มรันบอท
app.run_polling()