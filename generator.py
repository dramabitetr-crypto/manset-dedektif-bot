import json
import os
import subprocess
import requests
from PIL import Image, ImageDraw, ImageFont

# 1. State dosyasını oku
if os.path.exists('state.json'):
    with open('state.json', 'r', encoding='utf-8') as f:
        state = json.load(f)
else:
    state = {"last_index": 0}

currentIndex = state.get("last_index", 0)

# 2. Vakalar.json dosyasını oku
with open('vakalar.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

current_case = cases[currentIndex % len(cases)]
print(f"İşlenen Vaka: {current_case['title']}")

title_text = current_case['title']
clean_content = current_case['content'].replace('<b>', '').replace('</b>', '').replace('<br>', '\n')

# Font yolları (Linux sunucu desteği)
font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

try:
    title_font = ImageFont.truetype(font_bold, 50)
    content_font = ImageFont.truetype(font_regular, 36)
    hook_font = ImageFont.truetype(font_bold, 42)
    timer_font = ImageFont.truetype(font_bold, 80)
    footer_font = ImageFont.truetype(font_regular, 32)
except:
    title_font = ImageFont.load_default()
    content_font = ImageFont.load_default()
    hook_font = ImageFont.load_default()
    timer_font = ImageFont.load_default()
    footer_font = ImageFont.load_default()

# 3. 55 Saniyelik Video İçin Kareleri (Frames) Üretelim (25 fps * 55 sn = ~1375 kare)
# Disk alanını verimli kullanmak için geçici klasör açıyoruz
os.makedirs("frames", exist_ok=True)

FPS = 25
TOTAL_SECONDS = 55
TOTAL_FRAMES = FPS * TOTAL_SECONDS

print(f"{TOTAL_SECONDS} saniyelik dinamik video kareleri oluşturuluyor...")

for frame_idx in range(TOTAL_FRAMES):
    # Arka plan: Koyu dedektif mavisi/grisi gradient hissi veren düz ton
    img = Image.new('RGB', (1080, 1920), color='#070b14')
    d = ImageDraw.Draw(img)
    
    # Üst Kanca (Hook) - İzleyicinin dikkatini çeken soru
    d.text((70, 150), "🚨 DİKKAT! BU VAKA ÇÖZÜLMEYİ BEKLİYOR", fill="#38bdf8", font=hook_font)
    
    # Başlık
    d.text((70, 240), title_text, fill="#fbbf24", font=title_font)
    
    # Çizgi Ayırıcı
    d.line([(70, 330), (1010, 330)], fill="#1e293b", width=4)
    
    # Vaka Metni (Okunabilir geniş alan)
    d.text((70, 380), clean_content, fill="#f8fafc", font=content_font)
    
    # Geri Sayım Mantığı (Örn: 50. saniyeden 0'a doğru geriye sayan dinamik sayaç)
    # 55 saniyelik videoda son 30 saniye sayaç aktif olsun
    current_sec = frame_idx // FPS
    remaining_time = max(0, 30 - current_sec) if current_sec >= 25 else 30
    
    # Sayaç Kutusu ve Metni (Altta dikkat çekici alan)
    d.rounded_rectangle([(70, 1350), (1010, 1520)], radius=20, fill="#111827", outline="#ef4444", width=3)
    d.text((110, 1380), f"⏳ SÜRE: {remaining_time:02d} SANİYE", fill="#ef4444", font=timer_font)
    
    # Çağrı (Call to Action) - Mini App Yönlendirmesi
    d.text((70, 1600), "Cevabı buldun mu?\nTelegram Mini App üzerinden çözümü aç ve oyuna katıl! 👇\nt.me/manset_dedektif_bot/dedektif", fill="#38bdf8", font=footer_font)
    
    # Her kareyi sırayla kaydet (örn: frame_0001.png)
    frame_name = os.path.join("frames", f"frame_{frame_idx:04d}.png")
    img.save(frame_name)

print("Kareler tamamlandı, FFmpeg ile video ve ses birleştiriliyor...")

# 4. FFmpeg ile Kareleri ve (varsa) Gerilim Müziğini Birleştir
video_path = "gunun_vakasi.mp4"

# Gerilim atmosferi için telifsiz kısa bir ambient/gerilim ses efekti ekleyebiliriz
# Veya şimdilik kusursiz akıcı 55 saniyelik sessiz/ritimli dikey video üretelim:
ffmpeg_command = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", "frames/frame_%04d.png",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-crf", "23",
    video_path
]

subprocess.run(ffmpeg_command, check=True)
print("Dinamik dedektif videosu başarıyla üretildi!")

# 5. Telegram Kanalına Videoyu Gönder
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, 'rb') as video_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': f"🎬 GÜNÜN DEDEKTİFİK VAKASI (Süre: 55sn)\n\n{title_text}\n\n🕵️ Oyuna katılmak ve çözmek için Mini App'e tıkla!"
        }
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
        print("Telegram Yanıtı:", response.text)

# 6. Index'i artır ve kaydet
state["last_index"] = currentIndex + 1
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=4)

print("İşlem tamamlandı!")
