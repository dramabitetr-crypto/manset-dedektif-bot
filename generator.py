import json
import os
import subprocess
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

# Sıradaki vakayı seç (100 biterse baştan başla)
current_case = cases[currentIndex % len(cases)]
print(f"İşlenen Vaka: {current_case['title']}")

# 3. Dikey Video için Arka Plan Görseli Oluştur (9:16 - 1080x1920)
img = Image.new('RGB', (1080, 1920), color='#0f172a')
d = ImageDraw.Draw(img)

title_text = current_case['title']
clean_content = current_case['content'].replace('<b>', '').replace('</b>', '').replace('<br>', '\n')

# Metin yerleşimi
d.text((80, 250), title_text, fill="#f59e0b", font_size=55)
d.text((80, 420), clean_content, fill="#f8fafc", font_size=40)
d.text((80, 1350), "❓ KİM BU İŞLEDİ?", fill="#ef4444", font_size=50)
d.text((80, 1500), "Cevap ve Oyunu Çözmek İçin:\nTelegram Mini App'e Tıkla! 👇\nt.me/manset_dedektif_bot/dedektif", fill="#38bdf8", font_size=38)

# Geçici görsel olarak kaydet
image_path = "temp_frame.png"
img.save(image_path)

# 4. FFmpeg kullanarak görseli 7 saniyelik dikey MP4 videoya dönüştür
video_path = "gunun_vakasi.mp4"
ffmpeg_command = [
    "ffmpeg", "-y",
    "-loop", "1",
    "-i", image_path,
    "-t", "7",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-vf", "scale=1080:1920",
    video_path
]

print("Video oluşturuluyor...")
subprocess.run(ffmpeg_command, check=True)
print("Video başarıyla üretildi!")

# 5. Telegram'a Videoyu Gönder
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, 'rb') as video_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': f"🎬 Yeni Günün Dedektiflik Videosu!\n\n{title_text}\n\nOyuna katılmak için profildeki linke tıkla!"
        }
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
        print("Telegram Yanıtı:", response.text)

# 6. Endeks numarasını bir artır ve state.json'a kaydet
state["last_index"] = currentIndex + 1
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=4)

print("Vaka başarıyla işlendi ve video gönderildi!")
