from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# ฟังก์ชันที่จะตอบกลับเมื่อพิมพ์ /start
async def start(update: Update, context):
    await update.message.reply_text(f'Hello {update.effective_user.first_name}, welcome to my bot!')

# ใส่ API Token ของคุณที่นี่
TOKEN = 'YOUR_REAL_BOT_API_TOKEN'

# สร้างแอปพลิเคชันบอท
app = ApplicationBuilder().token(TOKEN).build()

# เพิ่มคำสั่ง /start ให้บอท
app.add_handler(CommandHandler("start", start))

# เริ่มบอท
app.run_polling()