import asyncio
import json
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart

# ================= SOZLAMALAR =================
BOT_TOKEN = "8882224852:AAFGI68hb5dVwlICwB_giFAq1WffaDhMZcw"
ADMIN_ID = 123456789  # O'zingizning Telegram raqamli ID'ingiz (int formatda)
DB_FILE = "movies.json"
# ===============================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def load_movies():
    """Bazadagi kinolarni o'qish"""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_movies(data):
    """Kinolarni bazaga yozish"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Start buyrug'i berilganda"""
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Kinoni ko'rish uchun uning **kodini** yuboring (masalan: `101`)."
    )


@dp.message(Command("add"))
async def add_movie_handler(message: types.Message):
    """Admin kino qo'shishi uchun buyruq"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu buyruq faqat bot admini uchun!")
        return

    video = None
    code = None
    caption = ""

    # Agar videoning o'zi bilan birga /add yuborilgan bo'lsa
    if message.video:
        video = message.video
        caption_text = message.caption or ""
        parts = caption_text.split(maxsplit=2)
        if len(parts) >= 2:
            code = parts[1]
            caption = parts[2] if len(parts) > 2 else ""

    # Agar avval yuborilgan videoga reply (javob) qilib /add yozilgan bo'lsa
    elif message.reply_to_message and message.reply_to_message.video:
        video = message.reply_to_message.video
        parts = message.text.split(maxsplit=2)
        if len(parts) >= 2:
            code = parts[1]
            caption = parts[2] if len(parts) > 2 else (message.reply_to_message.caption or "")

    if not video or not code:
        await message.answer(
            "⚠️ Kinoni to'g'ri saqlash bo'yicha ko'rsatma:\n\n"
            "1. Videoni yuborishda izohiga: `/add 101 Film nomi` deb yozing.\n"
            "2. Yoki videoga javob (reply) tarzida: `/add 101 Film nomi` deb yuboring."
        )
        return

    movies = load_movies()
    movies[code] = {
        "file_id": video.file_id,
        "caption": caption
    }
    save_movies(movies)

    await message.answer(f"✅ Kino muvaffaqiyatli saqlandi!\n🔑 Kodi: <b>{code}</b>", parse_mode="HTML")


@dp.message(F.text)
async def get_movie_handler(message: types.Message):
    """Foydalanuvchi kod yuborganida kinoni topib berish"""
    code = message.text.strip()
    movies = load_movies()

    if code in movies:
        movie = movies[code]
        file_id = movie.get("file_id")
        caption = movie.get("caption", "")
        await message.reply_video(video=file_id, caption=caption)
    else:
        await message.answer("❌ Bunday kodli kino topilmadi. Kodni to'g'ri kiritganingizni tekshiring.")


async def main():
    print("Bot serverda muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
