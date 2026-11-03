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
    title_font = ImageFont.truetype(font_bold, 44)
    content_font = ImageFont.truetype(font_regular, 30)
    hook_font = ImageFont.truetype(font_bold, 36)
    scene_title_font = ImageFont.truetype(font_bold, 38)
    timer_font = ImageFont.truetype(font_bold, 32)
    footer_font = ImageFont.truetype(font_regular, 26)
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

print(f"{TOTAL_SECONDS} saniyelik çok sahneli apartman dedektif video kareleri oluşturuluyor...")

for frame_idx in range(TOTAL_FRAMES):
    current_sec = frame_idx / FPS
    
    # Derin ve karanlık bina atmosferi arka planı
    img = Image.new('RGB', (1080, 1920), color='#04060b')
    d = ImageDraw.Draw(img)
    
    # --- SAĞ ÜST KÖŞE: Minimalist Dijital Sayaç (Son 15 saniyede aktif) ---
    if current_sec >= 40:
        rem_time = max(0, int(55 - current_sec))
        # Şık köşe hap kutusu sayaç
        d.rounded_rectangle([(820, 40), (1040, 110)], radius=15, fill="#18181b", outline="#ef4444", width=3)
        d.text((850, 57), f"⏳ 0:{rem_time:02d}", fill="#ef4444", font=timer_font)
    else:
        d.rounded_rectangle([(820, 40), (1040, 110)], radius=15, fill="#18181b", outline="#38bdf8", width=2)
        d.text((845, 57), "🔍 DOSYA AÇIK", fill="#38bdf8", font=footer_font)

    # Üst Bilgi Şeridi
    d.rectangle([(0, 0), (790, 120)], fill="#0f172a")
    d.text((40, 40), "🏢 7 NUMARALI DAİRENİN SIRRI", fill="#38bdf8", font=hook_font)

    # --- ZAMAN ÇİZELGESİNE GÖRE SAHNE DEĞİŞİMLERİ (Multi-Scene) ---
    
    if current_sec < 10:
        # --- SAHNE 1: GİRİŞ / KANCA ---
        scene_title = "🚨 GİZEMLİ ÇAĞRI"
        box_color = "#1e1b4b"
        border_color = "#6366f1"
        
        narrative = (
            "Sessiz ve sakin bir sokaktaki 6 daireli bu apartmanda, "
            "sadece geceleri çalan gizemli bir 7. zil var...\n\n"
            "Ancak o numarada resmi olarak kimse yaşamıyor. "
            "Dün gece o daireden gelen seslerle tüm bina ayağa kalktı."
        )
    elif current_sec < 30:
        # --- SAHNE 2: OLAY ÖZETİ & DETAYLAR ---
        scene_title = f"📁 {title_text}"
        box_color = "#0b1329"
        border_color = "#fbbf24"
        
        # Metni otomatik olarak sığdırma (Text Wrap)
        wrapped_lines = textwrap.wrap(full_story, width=42)
        narrative = "\n".join(wrapped_lines[:12]) # Ekrana sığacak kadar satır
    else:
        # --- SAHNE 3: ŞÜPHELİLER VE KARAR ANI ---
        scene_title = "🔍 ŞÜPHELİLER ARASINDA KİM VAR?"
        box_color = "#111827"
        border_color = "#f43f5e"
        
        narrative = (
            "A) Zemin Kattaki Müdür: 'Sesi duydum ama odadan çıkmadım.' diyor.\n\n"
            "B) 2. Kattaki Komşu: O saatte çöp attığını iddia ediyor.\n\n"
            "C) Boş olduğu bilinen 3. kattan gelen sıcak kahve kokusu...\n\n"
            "Katil bu binanın sakinlerinden biri. Deliller birleşti!"
        )

    # Sahne Kutusu Çizimi
    d.rounded_rectangle([(50, 170), (1030, 1350)], radius=20, fill=box_color, outline=border_color, width=3)
    
    # Sahne Başlığı
    d.text((90, 220), scene_title, fill="#fbbf24", font=scene_title_font)
    d.line([(90, 280), (990, 280)], fill="#334155", width=2)
    
    # Sahne İçerik Metni
    d.text((90, 340), narrative, fill="#f8fafc", font=content_font)

    # --- ALT KISIM: Sabit Çağrı (Call to Action) ---
    d.rounded_rectangle([(50, 1420), (1030, 1850)], radius=15, fill="#0c4a6e", outline="#38bdf8", width=2)
    cta_title = "🎯 KARARINI VER DEDEKTİF!"
    cta_desc = (
        "Katili bulduysan şüphelinin adını (A, B veya C) seç,\n"
        "hemen Telegram Mini App'e gir ve dosyayı kapat! 👇\n\n"
        "t.me/manset_dedektif_bot/dedektif"
    )
    d.text((90, 1470), cta_title, fill="#38bdf8", font=hook_font)
    d.text((90, 1550), cta_desc, fill="#e0f2fe", font=content_font)

    # Kareyi kaydet
    frame_name = os.path.join("frames", f"frame_{frame_idx:04d}.png")
    img.save(frame_name)

print("Tüm apartman sahneleri tamamlandı, FFmpeg ile video derleniyor...")

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
print("Apartman Sırrı dedektif videosu başarıyla üretildi!")

# 5. Telegram Kanalına Videoyu Gönder
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    with open(video_path, 'rb') as video_file:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': f"🏢 APARTMAN SIRRI: {title_text}\n\n🕵️ 7 numaralı dairenin sırrını çözebilecek misin? Mini App'e tıkla!\nt.me/manset_dedektif_bot/dedektif"
        }
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
        print("Telegram Yanıtı:", response.text)

# 6. Index'i artır ve kaydet
state["last_index"] = currentIndex + 1
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=4)

print("İşlem başarıyla tamamlandı!")
