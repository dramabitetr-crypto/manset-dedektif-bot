import json
import os
import requests
from PIL import Image, ImageDraw, ImageFont

# 1. State (Kaldığımız yer) dosyasını oku
if os.path.exists('state.json'):
    with open('state.json', 'r', encoding='utf-8') as f:
        state = json.load(f)
else:
    state = {"last_index": 0}

currentIndex = state.get("last_index", 0)

# 2. Vakalar.json dosyasını oku
with open('vakalar.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

# Sıradaki vakayı seç (100 biterse başa dön)
current_case = cases[currentIndex % len(cases)]
print(f"İşlenen Vaka: {current_case['title']}")

# 3. Dikey Video Görseli Oluştur (9:16 - 1080x1920)
img = Image.new('RGB', (1080, 1920), color='#0f172a')
d = ImageDraw.Draw(img)

# Metinleri ekrana çizdirme hazırlığı
title_text = current_case['title']
# HTML etiketlerini temizleyerek sade metin elde edelim
clean_content = current_case['content'].replace('<b>', '').replace('</b>', '').replace('<br>', '\n')

# Basit bir metin yerleşimi
d.text((80, 200), title_text, fill="#f59e0b", font_size=50)
d.text((80, 350), clean_content, fill="#f8fafc", font_size=35)
d.text((80, 1400), "Cevap Telegram Mini App'te!\nt.me/manset_dedektif_bot/dedektif", fill="#38bdf8", font_size=40)

# Görseli geçici olarak kaydet
image_path = "output_case.png"
img.save(image_path)

# (İsteğe bağlı veya FFmpeg ile video dönüştürme adımı buraya eklenebilir)
# Şimdilik doğrudan görseli veya üretilen videoyu Telegram'a gönderelim:

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(image_path, 'rb') as photo_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': f"🎯 Yeni Günün Vakası!\n\n{title_text}\n\nOyuna katılmak için profildeki linke tıkla!"
        }
        files = {'photo': photo_file}
        response = requests.post(url, data=payload, files=files)
        print("Telegram Yanıtı:", response.text)

# 4. Endeks numarasını bir artır ve state.json'a kaydet
state["last_index"] = currentIndex + 1
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=4)

print("Vaka başarıyla işlendi ve sıradaki adıma geçildi!")
