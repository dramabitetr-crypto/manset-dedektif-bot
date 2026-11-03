import json
import os
import subprocess
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

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

title_text = str(current_case.get('title', 'Apartman Sırrı'))
raw_content = current_case.get('content', 'Detaylar gizlidir...')

if isinstance(raw_content, list):
    full_story = "\n".join([str(item) for item in raw_content])
else:
    full_story = str(raw_content).replace('<b>', '').replace('</b>', '').replace('<br>', '\n')

# 3. Seslendirme (TTS) Metnini Oluştur
speech_text = (
    f"Dikkat dedektif! Yeni vaka dosyası: {title_text}. "
    f"Saat gece yarısını geçiyordu. Apartmanın karanlık koridorlarında gerilim tırmanıyor. "
    f"{full_story} "
    f"Şüpheliler inceleme altında. Süre daralıyor! "
    f"Katili bulduysan şüphelinin harfini hemen yorumlara yaz ve Telegram Mini App'ten dosyayı mühürle!"
)

print("Yapay zeka seslendirmesi üretiliyor...")
tts = gTTS(text=speech_text, lang='tr', slow=False)
audio_path = "voiceover.mp3"
tts.save(audio_path)

# Ses dosyasının saniyesini hassas şekilde ölçelim
probe = subprocess.run([
    "ffprobe", "-v", "error", "-show_entries",
    "format=duration", "-of",
    "default=noprint_wrappers=1:nokey=1", audio_path
], stdout=subprocess.PIPE, text=True)

try:
    audio_duration = float(probe.stdout.strip())
except:
    audio_duration = 45.0

# Video süresini ses dosyasına tam eşitleyelim (en az 40 saniye)
TOTAL_SECONDS = max(40, int(audio_duration) + 2)
FPS = 25
TOTAL_FRAMES = FPS * TOTAL_SECONDS
print(f"Seslendirme tamamlandı. Toplam Video Süresi: {TOTAL_SECONDS} saniye.")

# Font yolları (Linux sunucu desteği)
font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

try:
    title_font = ImageFont.truetype(font_bold, 42)
    content_font = ImageFont.truetype(font_regular, 28)
    hook_font = ImageFont.truetype(font_bold, 34)
    scene_title_font = ImageFont.truetype(font_bold, 36)
    timer_font = ImageFont.truetype(font_bold, 30)
    footer_font = ImageFont.truetype(font_regular, 24)
except:
    title_font = ImageFont.load_default()
    content_font = ImageFont.load_default()
    hook_font = ImageFont.load_default()
    scene_title_font = ImageFont.load_default()
    timer_font = ImageFont.load_default()
    footer_font = ImageFont.load_default()

os.makedirs("frames", exist_ok=True)
print("Gerilim sahneleri kareleri oluşturuluyor...")

def draw_thriller_background(d, scene_type, frame_idx):
    # Kan donduran karanlık arka plan
    d.rectangle([(0, 0), (1080, 1920)], fill="#020408")
    
    if scene_type == 1:
        d.rectangle([(0, 0), (1080, 150)], fill="#450a0a") # Korku Kırmızısı
    else:
        d.rectangle([(0, 0), (1080, 150)], fill="#090d16") # Gizem Mavisi

    d.rectangle([(120, 450), (960, 1850)], fill="#090e1a", outline="#1e293b", width=4)
    
    floor_height = 200
    start_y = 520
    
    for floor in range(6):
        y = start_y + (floor * floor_height)
        d.line([(120, y - 20), (960, y - 20)], fill="#1e293b", width=2)
        
        for win in range(3):
            wx = 180 + (win * 260)
            wy = y
            if floor == 4 and scene_type == 1:
                win_color = "#ef4444" if (frame_idx // 10) % 2 == 0 else "#7f1d1d"
            elif floor == 1 and scene_type == 2:
                win_color = "#38bdf8"
            else:
                win_color = "#b45309" if (floor + win + frame_idx // 25) % 3 == 0 else "#0f172a"
            d.rounded_rectangle([(wx, wy), (wx + 110, wy + 130)], radius=10, fill=win_color)

    if scene_type == 2:
        # Büyüteç ve Fincan Çizimi
        d.ellipse([(800, 250), (920, 370)], outline="#38bdf8", width=8)
        d.line([(890, 340), (950, 400)], fill="#38bdf8", width=8)
        d.rounded_rectangle([(150, 280), (220, 360)], radius=6, fill="#334155")
        d.arc([(210, 290), (250, 340)], start=270, end=90, fill="#334155", width=5)

for frame_idx in range(TOTAL_FRAMES):
    current_sec = frame_idx / FPS
    
    # Süreye oranlı dinamik sahne geçişleri
    phase_1 = TOTAL_SECONDS * 0.25
    phase_2 = TOTAL_SECONDS * 0.70
    
    if current_sec < phase_1:
        scene_type = 1
        scene_title = "⚠️ KAN DONDURAN ÇIĞLIK!"
        narrative = (
            "Saat gece yarısını çoktan geçiyordu...\n"
            "Apartmanın karanlık koridorlarında o acımasız ayak sesleri "
            "yankılandığında, herkes uykudaydı ama o... uyanıktı.\n\n"
            "7 numaralı gizli daireden gelen panik dolu fısıltılar "
            "biraz sonra işlenecek cinayetin habercisiydi."
        )
        box_bg = "#180505"
        border_col = "#dc2626"
    elif current_sec < phase_2:
        scene_type = 2
        scene_title = f"📁 DELİL DOSYASI: {title_text}"
        wrapped_lines = textwrap.wrap(full_story, width=40)
        narrative = "\n".join(wrapped_lines[:10])
        box_bg = "#08101d"
        border_col = "#38bdf8"
    else:
        scene_type = 3
        scene_title = "🔍 ŞÜPHELİLER ÇEMBERİ"
        narrative = (
            "A) Zemin Kattaki Müdür: 'O saatte uyuyordum' diyor ama elleri titriyor.\n\n"
            "B) 2. Kattaki Komşu: Elindeki lekeli bezi gizlemeye çalışıyor.\n\n"
            "C) Boş olduğu bilinen daireden gelen taze kahve kokusu...\n\n"
            "Süre daralıyor dedektif! Katil bu binanın içinde."
        )
        box_bg = "#111827"
        border_col = "#f43f5e"

    img = Image.new('RGB', (1080, 1920), color='#020408')
    d = ImageDraw.Draw(img)
    draw_thriller_background(d, scene_type, frame_idx)

    # Sağ üst köşe sayaç (Son 15 saniyede aktif)
    if current_sec >= (TOTAL_SECONDS - 15):
        rem_time = max(0, int(TOTAL_SECONDS - current_sec))
        d.rounded_rectangle([(800, 40), (1040, 110)], radius=15, fill="#18181b", outline="#ef4444", width=3)
        d.text((830, 57), f"⏳ 0:{rem_time:02d}", fill="#ef4444", font=timer_font)
    else:
        d.rounded_rectangle([(800, 40), (1040, 110)], radius=15, fill="#18181b", outline="#38bdf8", width=2)
        d.text((825, 57), "🔎 GİZLİ DOSYA", fill="#38bdf8", font=footer_font)

    d.rectangle([(0, 0), (770, 110)], fill="#0b0f19")
    d.text((40, 35), "🩸 MANŞET DEDEKTİF | GERİLİM SERİSİ", fill="#ef4444" if scene_type==1 else "#38bdf8", font=hook_font)

    d.rounded_rectangle([(60, 1120), (1020, 1580)], radius=20, fill=box_bg, outline=border_col, width=3)
    d.text((100, 1155), scene_title, fill="#fbbf24", font=scene_title_font)
    d.line([(100, 1215), (980, 1215)], fill="#334155", width=2)
    d.text((100, 1245), narrative, fill="#f8fafc", font=content_font)

    d.rounded_rectangle([(60, 1610), (1020, 1880)], radius=15, fill="#0c4a6e", outline="#38bdf8", width=2)
    cta_title = "🎯 KATİLİ BULDUN MU?"
    cta_desc = (
        "Cevabı bulduysan şüphelinin harfini (A, B veya C) hemen\n"
        "yorumlar kısmına yaz, Telegram Mini App'ten dosyayı mühürle! 👇\n\n"
        "t.me/manset_dedektif_bot/dedektif"
    )
    d.text((100, 1645), cta_title, fill="#38bdf8", font=hook_font)
    d.text((100, 1715), cta_desc, fill="#e0f2fe", font=content_font)

    frame_name = os.path.join("frames", f"frame_{frame_idx:04d}.png")
    img.save(frame_name)

print("Kareler tamamlandı, FFmpeg ile ses ve görüntü birleştiriliyor...")

# 4. FFmpeg ile Görüntü ve Seslendirmeyi Birleştirme
video_path = "gunun_vakasi.mp4"
ffmpeg_command = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", "frames/frame_%04d.png",
    "-i", audio_path,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    video_path
]

subprocess.run(ffmpeg_command, check=True)
print("Seslendirmeli gerilim videosu başarıyla üretildi!")

# 5. Telegram'a Gönderim
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, 'rb') as video_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': f"🩸 SESLENDİRMELİ VAKA: {title_text}\n\n🕵️ Katili bulduysan yorumlara yaz ve Mini App'ten çöz!\nt.me/manset_dedektif_bot/dedektif"
        }
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
        print("Telegram Yanıtı:", response.text)

# 6. Index Güncelleme
state["last_index"] = currentIndex + 1
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=4)

print("İşlem başarıyla tamamlandı!")
