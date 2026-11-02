import os
import asyncio
from telegram import Bot

# Gizli kasadan (GitHub Secrets) token'ı alıyoruz
TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def send_daily_case():
    bot = Bot(token=TOKEN)
    
    # Günün vakası metni
    vaka_metni = (
        "🕵️ **GÜNÜN VAKASI: Antika Saat Hırsızlığı**\n\n"
        "Sabah 10:00'da dükkana gelindiğinde altın saat yerinde yoktu. "
        "Kapıda zorlama yok, alarm çalmadı!\n\n"
        "🔍 **Şüpheliler:**\n"
        "1. Kerem (Ortak - Kısa süreliğine dışarı çıktı)\n"
        "2. Canan (Temizlikçi - Dün hastaydım diyor ama anahtar çelişkisi var)\n"
        "3. Mert (Çırak - Sabah uyuyakalmış)\n\n"
        "Sence hırsız kim? Cevabını düşün!"
    )
    
    # Buraya kendi Telegram kullanıcı ID'ni veya test grubunun ID'sini yazabilirsin
    # Örnek olarak kendi chat_id'ni buraya koyabilirsin
    # Şimdilik yapıyı kuruyoruz:
    print("Vaka metni hazır, Telegram'a gönderiliyor...")

if __name__ == "__main__":
    asyncio.run(send_daily_case())
