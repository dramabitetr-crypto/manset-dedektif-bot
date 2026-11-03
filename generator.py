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
print(f"İşlenen Vaka: {current_case.get('title', 'Bilinmeyen Vaka')}")

title_text = str(current_case.get('title', 'Dedektiflik Vakası'))
raw_content = current_case.get('content', 'Detaylar gizlidir...')

# Metinlerin kesinlikle string (metin) olmasını sağlıyoruz (Hata önleyici)
if isinstance(raw_content, list):
    clean_content = "\n".join([str(item) for item in raw_content])
else:
    clean_content = str(raw_content).replace('<b>', '').replace('</b>', '').replace('<br>', '\n')

raw_suspects = current_case.get('suspects', "🔍 Şüpheliler: Arşiv Sorumlusu, Gece Bekçisi, Araştırmacı")
if isinstance(raw_suspects, list):
    suspects_text = "🔍 Şüpheliler:\n" + "\n".join([f"- {s}" for s in raw_suspects])
else:
    suspects_text = str(raw_suspects)

# Font yolları (Linux sunucu desteği)
font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

try:
    title_font = ImageFont.truetype(font_bold, 48)
    content_font = ImageFont.truetype(font_regular, 32)
    hook_font = ImageFont.truetype(font_bold, 38)
    timer_font = ImageFont.truetype(font_bold, 75)
    footer_font = ImageFont.truetype(font_regular, 30)
except:
    title_font = ImageFont.load_default()
    content_font = ImageFont.load_default()
    hook_font = ImageFont.load_default()
    timer_font = ImageFont.load_default()
    footer_font = ImageFont.load_default()

# 3. 55 Saniyelik Video İçin Kareleri (Frames) Üretelim (25 fps * 55 sn = 1375 kare)
os.makedirs("frames", exist_ok=True)

FPS = 25
TOTAL_SECONDS = 55
TOTAL_FRAMES = FPS * TOTAL_SECONDS

print(f"{TOTAL_SECONDS} saniyelik zenginleştirilmiş dedektif video kareleri oluşturuluyor...")

for frame_idx in range(TOTAL_FRAMES):
    current_sec = frame_idx / FPS
    
    # Arka plan: Derin dedektif koyu tonu
    img = Image.new('RGB', (1080, 1920), color='#050811')
    d = ImageDraw.Draw(img)
    
    # Dekoratif Üst Çerçeve / Şerit
    d.rectangle([(0, 0), (1080, 120)], fill="#0f172a")
    d.text((50, 40), "🔎 MANŞET DEDEKTİF | GİZLİ DOSYA ARŞİVİ", fill="#38bdf8", font=hook_font)
    
    # --- AŞAMA 1: Giriş Kancası (İlk 8 saniye boyunca ekranda sesleniş) ---
    if current_sec < 8:
        d.rounded_rectangle([(50, 180), (1030, 450)], radius=15, fill="#1e1b4b", outline="#6366f1", width=3)
        d.text((90, 220), "📢 DEDEKTİF, DİKKATİNİ BURAYA VER!", fill="#c7d2fe", font=hook_font)
        intro_msg = "Sessiz bir mekanda kusursuz bir cinayet işlendi.\nDeliller ortada, fakat katil aramızda saklanıyor.\nDosyayı dikkatle incele ve katili bul!"
        d.text((90, 290), intro_msg, fill="#e2e8f0", font=content_font)
    else:
        # --- AŞAMA 2: Vaka Detayları ve Şüpheliler Ekranı ---
        # Başlık Kutusu
        d.rounded_rectangle([(50, 160), (1030, 310)], radius=15, fill="#0f172a", outline="#fbbf24", width=2)
        d.text((80, 190), title_text, fill="#fbbf24", font=title_font)
        
        # Olay Metni Alanı
        d.rounded_rectangle([(50, 330), (1030, 950)], radius=15, fill="#0b1329", outline="#334155", width=2)
        d.text((80, 370), "📜 OLAY ÖZETİ & İPUÇLARI:", fill="#38bdf8", font=hook_font)
        d.text((80, 440), clean_content, fill="#f8fafc", font=content_font)
        
        # Şüpheliler Alanı
        d.rounded_rectangle([(50, 980), (1030, 1220)], radius=15, fill="#111827", outline="#f43f5e", width=2)
        d.text((80, 1015), suspects_text, fill="#fca5a5", font=content_font)

    # --- AŞAMA 3: Geri Sayım Mantığı (Son 30 saniyede devreye girer) ---
    if current_sec >= 25:
        remaining_time = max(0, int(55 - current_sec))
        d.rounded_rectangle([(50, 1330), (1030, 1530)], radius=20, fill="#18181b", outline="#ef4444", width=4)
        d.text((90, 1365), f"⏳ KARAR İÇİN SON: {remaining_time:02d} SANİYE", fill="#ef4444", font=timer_font)
    else:
        d.rounded_rectangle([(50, 1330), (1030, 1530)], radius=20, fill="#18181b", outline="#38bdf8", width=2)
        d.text((90, 1390), "🔍 İpuçlarını İncele ve Düşün...", fill="#38bdf8", font=title_font)

    # --- AŞAMA 4: Alt Çağrı (Call to Action) ---
    d.rounded_rectangle([(50, 1580), (1030, 1850)], radius=15, fill="#0c4a6e", outline="#38bdf8", width=2)
    cta_text = "Katil kim? Çözümü görmek ve oyuna katılmak için\nTelegram Mini App'e tıkla! 👇\nt.me/manset_dedektif_bot/dedektif"
    d.text((90, 1630), cta_text, fill="#e0f2fe", font=content_font)

    # Her kareyi kaydet
    frame_name = os.path.join("frames", f"frame_{frame_idx:04d}.png")
    img.save(frame_name)

print("Kareler tamamlandı, FFmpeg ile video oluşturuluyor...")

# 4. FFmpeg ile Kareleri Birleştir
video_path = "gunun_vakasi.mp4"
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
print("Profesyonel dedektif videosu başarıyla üretildi!")

# 5. Telegram Kanalına Videoyu Gönder
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, 'rb') as video_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': f"🎬 YENİ VAKA DOSYASI: {title_text}\n\n🕵️ Katili bulabilecek misin? Mini App üzerinden hemen çöz!\nt.me/manset_dedektif_bot/dedektif"
        }
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
        print("Telegram Yanıtı:", response.text)

# 6. Index'i artır ve kaydet
state["last_index"] = currentIndex + 1
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=4)

print("İşlem başarıyla tamamlandı!")
