import json
import os
import subprocess
import textwrap
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

title_text = str(current_case.get('title', 'Apartman Sırrı'))
raw_content = current_case.get('content', 'Detaylar gizlidir...')

if isinstance(raw_content, list):
    full_story = "\n".join([str(item) for item in raw_content])
else:
    full_story = str(raw_content).replace('<b>', '').replace('</b>', '').replace('<br>', '\n')

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

# 3. 55 Saniyelik Çok Sahneli Video İçin Kareler Üretiyoruz (25 fps * 55 sn = 1375 kare)
os.makedirs("frames", exist_ok=True)

FPS = 25
TOTAL_SECONDS = 55
TOTAL_FRAMES = FPS * TOTAL_SECONDS

print(f"{TOTAL_SECONDS} saniyelik kod tabanlı çizim sahneleri oluşturuluyor...")

def draw_programmatic_background(d, scene_type):
    """Kod ile binalar, gece gökyüzü, pencereler ve sokak atmosferi çizen fonksiyon"""
    # Gece Gökyüzü Arka Planı
    d.rectangle([(0, 0), (1080, 1920)], fill="#030712")
    
    # Ay
    d.ellipse([(850, 100), (970, 220)], fill="#fef08a")
    
    # Apartman Silüeti (Ana Bina)
    d.rectangle([(150, 500), (930, 1920)], fill="#0f172a", outline="#1e293b", width=4)
    
    # Katlar ve Pencereler (Kod ile 6 Kat + Gizemli 7. Kat)
    floor_height = 180
    start_y = 550
    
    for floor in range(7):
        y = start_y + (floor * floor_height)
        # Kat çizgisi
        d.line([(150, y - 20), (930, y - 20)], fill="#334155", width=2)
        
        # 4'er adet pencere çizimi
        for win in range(4):
            wx = 200 + (win * 180)
            wy = y
            
            # Renk belirleme (Bazı pencereler karanlık, bazıları sarı ışıklı)
            if floor == 0:  # Zemin kat
                win_color = "#38bdf8" if scene_type == 1 else "#1e293b"
            elif floor == 6: # Gizemli 7. Kat (Kırmızı/Tehlike ışığı)
                win_color = "#ef4444" if (scene_type == 3) else "#7f1d1d"
            else:
                win_color = "#fbbf24" if (floor + win) % 2 == 0 else "#1e293b"
                
            # Pencere kutusu
            d.rounded_rectangle([(wx, wy), (wx + 90, wy + 120)], radius=8, fill=win_color)

    # Sokak Zindanı / Zemin
    d.rectangle([(0, 1750), (1080, 1920)], fill="#020617")

for frame_idx in range(TOTAL_FRAMES):
    current_sec = frame_idx / FPS
    
    # Hikaye akışına göre sahne tipi seçimi (1, 2 veya 3)
    if current_sec < 12:
        scene_type = 1
        scene_title = "🏢 GECE YARISI APARTMANI"
        narrative = (
            "Sessiz ve sakin bir sokaktaki 6 daireli bu apartmanda,\n"
            "sadece geceleri çalan gizemli bir 7. zil var...\n\n"
            "Oysa o numarada resmi olarak kimse yaşamıyor.\n"
            "Dün gece o daireden gelen çığlıklarla tüm bina uyandı."
        )
        box_bg = "#1e1b4b"
        border_col = "#6366f1"
    elif current_sec < 35:
        scene_type = 2
        scene_title = f"📁 {title_text}"
        wrapped_lines = textwrap.wrap(full_story, width=42)
        narrative = "\n".join(wrapped_lines[:11])
        box_bg = "#0b1329"
        border_col = "#fbbf24"
    else:
        scene_type = 3
        scene_title = "🔍 ŞÜPHELİLER & KARAR ANI"
        narrative = (
            "A) Zemin Kattaki Müdür: 'Sesi duydum ama çıkmadım.'\n\n"
            "B) 2. Kattaki Komşu: O saatte çöp attığını iddia ediyor.\n\n"
            "C) Boş olduğu bilinen 7. kattan gelen sıcak ayak sesi...\n\n"
            "Katil bu binanın sakinlerinden biri. Deliller birleşti!"
        )
        box_bg = "#111827"
        border_col = "#f43f5e"

    # 1. Adım: Kod ile Çizilmiş Arka Planı Yükle
    img = Image.new('RGB', (1080, 1920), color='#030712')
    d = ImageDraw.Draw(img)
    draw_programmatic_background(d, scene_type)

    # 2. Adım: Üst Bilgi Şeridi ve Şık Dijital Köşe Sayaç
    if current_sec >= 40:
        rem_time = max(0, int(55 - current_sec))
        d.rounded_rectangle([(800, 40), (1040, 110)], radius=15, fill="#18181b", outline="#ef4444", width=3)
        d.text((830, 57), f"⏳ 0:{rem_time:02d}", fill="#ef4444", font=timer_font)
    else:
        d.rounded_rectangle([(800, 40), (1040, 110)], radius=15, fill="#18181b", outline="#38bdf8", width=2)
        d.text((825, 57), "🔍 DOSYA AÇIK", fill="#38bdf8", font=footer_font)

    d.rectangle([(0, 0), (770, 110)], fill="#0f172a")
    d.text((40, 35), "🏢 MANŞET DEDEKTİF | ÖZEL DOSYA", fill="#38bdf8", font=hook_font)

    # 3. Adım: Okunabilir Metin ve Hikaye Paneli
    d.rounded_rectangle([(60, 1150), (1020, 1600)], radius=20, fill=box_bg, outline=border_col, width=3)
    d.text((100, 1190), scene_title, fill="#fbbf24", font=scene_title_font)
    d.line([(100, 1250), (980, 1250)], fill="#334155", width=2)
    d.text((100, 1280), narrative, fill="#f8fafc", font=content_font)

    # 4. Adım: Alt Çağrı (Call to Action) Paneli
    d.rounded_rectangle([(60, 1630), (1020, 1880)], radius=15, fill="#0c4a6e", outline="#38bdf8", width=2)
    cta_title = "🎯 KARARINI VER DEDEKTİF!"
    cta_desc = (
        "Katili bulduysan şüphelinin adını (A, B veya C) seç,\n"
        "Telegram Mini App'e gir ve dosyayı kapat! 👇\n\n"
        "t.me/manset_dedektif_bot/dedektif"
    )
    d.text((100, 1665), cta_title, fill="#38bdf8", font=hook_font)
    d.text((100, 1735), cta_desc, fill="#e0f2fe", font=content_font)

    # Her kareyi kaydet
    frame_name = os.path.join("frames", f"frame_{frame_idx:04d}.png")
    img.save(frame_name)

print("Kod tabanlı apartman sahneleri tamamlandı, FFmpeg derleniyor...")

# 5. FFmpeg ile Video Üretimi
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
print("Programmatik dedektif videosu başarıyla üretildi!")

# 6. Telegram'a Gönderim
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, 'rb') as video_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': f"🏢 KOD TABANLI APARTMAN VAKASI: {title_text}\n\n🕵️ 7 numaralı dairenin sırrını çöz! Mini App'e tıkla:\nt.me/manset_dedektif_bot/dedektif"
        }
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
        print("Telegram Yanıtı:", response.text)

# 7. Index Güncelleme
state["last_index"] = currentIndex + 1
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=4)

print("İşlem başarıyla tamamlandı!")
