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
    
    # Canlı ve dikkat çekici format
    vaka_metni = (
        "🚨 <b>GÜNÜN KRİTİK VAKASI: #01</b> 🚨\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🏛️ <b>Olay Yeri:</b> Beyoğlu Antikacısı\n"
        "⏰ <b>Saat:</b> 10:00 (Sabah)\n\n"
        "💎 <b>Olay Özeti:</b>\n"
        "Vitrindeki paha biçilemez 19. yy altın cep saati yerinde yok! "
        "En garibi ise <b>kapıda hiç zorlama yok ve alarm asla çalmadı!</b>\n\n"
        "👥 <b>ŞÜPHELİLER:</b>\n"
        "1️⃣ <b>Kerem</b> (Dükkanın Ortağı)\n"
        "2️⃣ <b>Canan</b> (Temizlik Görevlisi)\n"
        "3️⃣ <b>Mert</b> (Çırak)\n\n"
        "🎯 <b>GÖREVİN:</b> Hırsız sence kim? Aşağıdaki butonlardan şüpheliyi seç ve dedektifliğini konuştur! 👇"
    )
    
    # Canlı ve renkli görünen interaktif butonlar
    keyboard = [
        [
            InlineKeyboardButton("🕵️ 1. Kerem (Ortak)", callback_data="yanlis_kerem"),
            InlineKeyboardButton("🧹 2. Canan (Temizlikçi)", callback_data="dogru_canan"),
        ],
        [
            InlineKeyboardButton("👦 3. Mert (Çırak)", callback_data="yanlis_mert"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # HTML formatı kullanarak daha net ve canlı görünmesini sağlıyoruz
    await bot.send_message(
        chat_id=CHAT_ID,
        text=vaka_metni,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    print("Canlı vaka ve butonlar başarıyla gönderildi!")

if __name__ == "__main__":
    asyncio.run(send_daily_case())
