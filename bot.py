import os
import asyncio
from telegram import Bot

# Gizli kasadan (GitHub Secrets) Token ve Chat ID'yi çekiyoruz
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def send_daily_case():
    # Bot nesnesini token ile oluşturuyoruz
    bot = Bot(token=TOKEN)
    
    # Göndereceğimiz gizemli vaka metni
    vaka_metni = (
        "🕵️ *MANŞET ARKASI: GÜNÜN VAKASI*\n\n"
        "*Vaka #01: Antika Saat Hırsızlığı*\n"
        "Sabah 10:00'da dükkana gelindiğinde altın saat yerinde yoktu. "
        "Kapıda zorlama yok, alarm hiç çalmadı!\n\n"
        "🔍 *Şüpheliler:*\n"
        "1️⃣ *Kerem (Ortak):* 'Kısa süreliğine kahve almaya çıktım' diyor.\n"
        "2️⃣ *Canan (Temizlikçi):* 'Dün hastaydım gelmedim' diyor ama anahtar çelişkisi var.\n"
        "3️⃣ *Mert (Çırak):* 'Sabah uyuyakalmışım' diyor.\n\n"
        "💡 *İpucu:* Vitrindeki camda sadece Canan'ın parmak izi var ama o her gün temizlik yapıyor. Hırsız kapıyı zorlamadan nasıl girdi?\n\n"
        "Sence katil/hırsız kim? Tahminini düşün!"
    )
    
    # Telegram'a mesajı gönderiyoruz
    await bot.send_message(
        chat_id=CHAT_ID,
        text=vaka_metni,
        parse_mode="Markdown"
    )
    print("Vaka başarıyla Telegram'a gönderildi!")

if __name__ == "__main__":
    asyncio.run(send_daily_case())
