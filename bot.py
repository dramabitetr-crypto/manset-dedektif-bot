import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# Gizli kasadan değerleri çekiyoruz
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def send_daily_case():
    if not CHAT_ID:
        print("HATA: TELEGRAM_CHAT_ID bulunamadı!")
        return

    bot = Bot(token=TOKEN)
    
    vaka_metni = (
        "🕵️ *MANŞET ARKASI: GÜNÜN VAKASI*\n\n"
        "*Vaka #01: Antika Saat Hırsızlığı*\n"
        "Sabah 10:00'da dükkana gelindiğinde altın saat yerinde yoktu. "
        "Kapıda zorlama yok, alarm hiç çalmadı!\n\n"
        "🔍 *Şüpheliler:*\n"
        "1️⃣ *Kerem (Ortak)*\n"
        "2️⃣ *Canan (Temizlikçi)*\n"
        "3️⃣ *Mert (Çırak)*\n\n"
        "💡 *Soru:* Hırsız sence kim? Aşağıdaki butonlardan tahminini seç!"
    )
    
    # İnteraktif butonları (Inline Keyboard) oluşturuyoruz
    # callback_data kısmı kullanıcı tıkladığında botun arkada anlayacağı koddur
    keyboard = [
        [
            InlineKeyboardButton("1️⃣ Kerem", callback_data="yanlis_kerem"),
            InlineKeyboardButton("2️⃣ Canan", callback_data="dogru_canan"),
        ],
        [
            InlineKeyboardButton("3️⃣ Mert", callback_data="yanlis_mert"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Mesajı butonlarla birlikte gönderiyoruz
    await bot.send_message(
        chat_id=CHAT_ID,
        text=vaka_metni,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    print("Vaka ve interaktif butonlar Telegram'a gönderildi!")

if __name__ == "__main__":
    asyncio.run(send_daily_case())
