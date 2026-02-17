import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Environment variables
API_ID = int(os.getenv("149.154.167.50:443"))
API_HASH = os.getenv("
-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEA6LszBcC1LGzyr992NzE0ieY+BSaOW622Aa9Bd4ZHLl+TuFQ4lo4g
5nKaMBwK/BIb9xUfg0Q29/2mgIR6Zr9krM7HjuIcCzFvDtr+L0GQjae9H0pRB2OO
62cECs5HKhT5DZ98K33vmWiLowc621dQuwKWSQKjWf50XYFw42h21P2KXUGyp2y/
+aEyZ+uVgLLQbRA1dEjSDZ2iGRy12Mk5gpYc397aYp438fsJoHIgJ2lgMv5h7WY9
t6N/byY9Nw9p21Og3AoXSL2q/2IJ1WRUhebgAdGVMlV1fkuOQoEzR7EdpqtQD9Cs
5+bfo3Nhmcyvk5ftB0WkJ9z6bNZ7yxrP8wIDAQAB
-----END RSA PUBLIC KEY-----")
BOT_TOKEN = os.getenv("8589260668:AAGKt7tl9e-7NulWzUFDcJerPnP7Ute55k4")

# Admin ID (o'zingizning Telegram ID)
ADMIN_ID = int(os.getenv("213110473"))

# Bot client
bot = Client("kino_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Simple in-memory database (replace with file/db in production)
films = {}  # {code: {"name": str, "parts": [link1, link2, ...]}}

# Inline keyboard helpers
def main_keyboard(user_id):
    if user_id == ADMIN_ID:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Kino Qo‘shish", callback_data="add_film")],
            [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
            [InlineKeyboardButton("👥 Adminlar", callback_data="admins")],
            [InlineKeyboardButton("❓ Yordam", callback_data="help")],
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Kino Qidirish", callback_data="search")],
            [InlineKeyboardButton("❓ Yordam", callback_data="help")],
        ])

# /start command
@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    await message.reply_text(
        f"🖐 Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "🔎 Kino kodini yuboring yoki menyudan tanlang:",
        reply_markup=main_keyboard(user_id)
    )

# Callback query handler
@bot.on_callback_query()
async def callbacks(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == "help":
        # Help menyusi
        help_text = f"📌 Qo‘llab-quvvatlash:\nAdmin: @{callback_query.from_user.username if user_id==ADMIN_ID else 'Yordamchi'}"
        await callback_query.message.edit_text(help_text, reply_markup=main_keyboard(user_id))

    elif data == "add_film" and user_id == ADMIN_ID:
        await callback_query.message.edit_text("📥 Kino qo‘shish:\nFilm nomini yuboring:")
        bot.set_parse_mode("html")
        bot.add_handler(filters.text, add_film_name)

    elif data == "search":
        await callback_query.message.edit_text("🔎 Kino nomi yoki kodini yuboring:")

# Handler for adding film name (admin)
async def add_film_name(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("⛔️ Faqat adminlar ishlata oladi!")
        return

    code = str(len(films)+1)
    films[code] = {"name": message.text, "parts": []}
    await message.reply_text(f"✅ Film qo‘shildi! Kod: {code}\nEndi qism linklarini yuboring (har birini alohida xabarda):")
    bot.add_handler(filters.text, lambda c, m: add_film_part(c, m, code))

async def add_film_part(client, message, code):
    if message.from_user.id != ADMIN_ID:
        return
    films[code]["parts"].append(message.text)
    await message.reply_text(f"✅ Qism qo‘shildi! Hozir {len(films[code]['parts'])} qism mavjud.\nYana qism qo‘shish uchun link yuboring yoki /done yozing.")

# Message handler for searching films
@bot.on_message(filters.text)
async def search_film(client, message):
    text = message.text.lower()
    found = []
    for code, film in films.items():
        if text in film["name"].lower() or text == code:
            parts = "\n".join(film["parts"])
            found.append(f"🎬 {film['name']} (Kod: {code})\n{parts}")
    if found:
        await message.reply_text("\n\n".join(found))
    else:
        await message.reply_text("❌ Film topilmadi!")

# Run the bot
bot.run()