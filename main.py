import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import Message
from aiogram.filters import Command
from api import TOKEN, ADMIN_ID, ADMIN_ID_S, ALLOWED_USERS

# 🔌 Flask va Thread
from flask import Flask
from threading import Thread

# Flask serverni ishga tushirish
app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Bot ishlayapti!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run_flask)
    thread.start()

# Log sozlash
logging.basicConfig(level=logging.INFO)

# Bot va dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Foydalanuvchi IDlarini saqlash
users = {}

# /start
@router.message(Command("start"))
async def handle_start(message: Message):
    await message.reply(
        "👋 Salom!\n\nMen sizning xabaringizni adminlarga yetkazuvchi yordamchingizman.\n"
        "📌 Buyruqlar:\n"
        "👥 /members – jamoa a'zolari haqida ma'lumot\n\n✨ Meni yaratgan inson – @theabduazimm!"
    )

# /links
@router.message(Command("links"))
async def handle_links(message: Message):
    links = (
        "🔗 <a href='https://www.youtube.com/@FabiDub_official'>YouTube kanali</a>\n"
        "📸 <a href='https://www.instagram.com/fabijon_uz/'>Instagram sahifasi</a>\n"
        "💬 <a href='https://t.me/FabiDub_official'>Telegram kanali</a>"
    )
    await message.reply(links, parse_mode="HTML", disable_web_page_preview=True)

# /members
@router.message(Command("members"))
async def handle_members(message: Message):
    await message.reply("Hali tayyor emas", parse_mode="HTML")

# /reply
@router.message(Command("reply"))
async def reply_message(message: Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply("Siz bu buyruqni ishlata olmaysiz.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Ishlatish: /reply <user_id> <текст>")
        return

    parts = args[1].split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Ishlatish: /reply <user_id> <текст>")
        return

    user_id = int(parts[0])
    reply_text = parts[1]

    try:
        await bot.send_message(user_id, f"<b>Admindan javob:</b>\n<i>{reply_text}</i>", parse_mode="HTML")
        await message.reply("Javob yuborildi.")
    except Exception as e:
        await message.reply(f"Jo'natishda xatolik: {e}")

# Har qanday xabarni adminlarga yuborish
@router.message()
async def forward_any_message(message: Message):
    user = message.from_user
    users[user.id] = user.username

    caption = (
        f"📩 <b>Yangi xabar!</b>\n"
        f"👤 <b>Kimdan:</b> @{user.username or 'No username'}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n\n"
        f"<b>Javob yozish:</b> <code>/reply {user.id} </code>"
    )

    if message.text:
        full_text = caption + f"\n\n💬 <b>Xabar:</b> \n{message.text}"
        await bot.send_message(ADMIN_ID, full_text, parse_mode="HTML")
        await bot.send_message(ADMIN_ID_S, full_text, parse_mode="HTML")
    else:
        if message.photo or message.voice or message.document:
            await message.forward(ADMIN_ID)
            await message.forward(ADMIN_ID_S)
            await bot.send_message(ADMIN_ID, caption, parse_mode="HTML")
            await bot.send_message(ADMIN_ID_S, caption, parse_mode="HTML")
        else:
            await message.forward(ADMIN_ID)
            await message.forward(ADMIN_ID_S)
            await bot.send_message(ADMIN_ID, caption + f"\n⚠️ <i>To'g'ridan-to'g'ri forward qilindi.</i>", parse_mode="HTML")
            await bot.send_message(ADMIN_ID_S, caption + f"\n⚠️ <i>To'g'ridan-to'g'ri forward qilindi.</i>", parse_mode="HTML")

# Polling boshlash
async def main():
    keep_alive()  # 👈 Flask serverni ishga tushirish
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
