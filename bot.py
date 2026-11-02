import os
import asyncio
from telegram import Bot

# Gizli kasadan değerleri çekiyoruz
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def send_daily_case():
    # Değerlerin okunup okunmadığını konsolda görelim
    print(f"TELEGRAM_TOKEN mevcut mü? {'Evet' if TOKEN else 'HAYIR!'}")
    print(f"TELEGRAM_CHAT_ID değeri: {CHAT_ID}")
    
    if not CHAT_ID:
        print("HATA: TELEGRAM_CHAT_ID boş veya okunamadı!")
        return

    bot = Bot(token=TOKEN)
    
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
    
    await bot.send_message(
        chat_id=CHAT_ID,
        text=vaka_metni,
        parse_mode="Markdown"
    )
    print("Vaka başarıyla Telegram'ına gönderildi!")

if __name__ == "__main__":
    asyncio.run(send_daily_case())
