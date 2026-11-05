import asyncio, json, os, sys, wave, subprocess, textwrap
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 1920, 24, 44100
LH, LY = 640, 540
FONT_YOL = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
HARF = "ABC"
RENK = [(60, 130, 235), (240, 140, 40), (150, 90, 220)]
_F = {}
def font(s):
    s = int(s)
    if s not in _F:
        f = None
        for p in FONT_YOL:
            if os.path.exists(p):
                f = ImageFont.truetype(p, s); break
        _F[s] = f or ImageFont.load_default()
    return _F[s]

def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()

def yaz(d, xy, t, size, fill=(255, 255, 255), anchor="mm", stroke=0, sf=(0, 0, 0)):
    d.text(xy, t, font=font(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sf)

_G = {}
def zemin(k):
    if k not in _G:
        a, b = {"hook": ((30, 6, 10), (6, 8, 20)), "ipucu": ((8, 14, 34), (14, 30, 58)),
                "ipucu2": ((10, 26, 30), (8, 12, 28)), "supheli": ((18, 10, 36), (6, 8, 20)),
                "oy": ((40, 8, 20), (8, 8, 30))}[k]
        t = np.linspace(0, 1, H)[:, None, None]
        arr = np.repeat(np.array(a) * (1 - t) + np.array(b) * t, W, axis=1).astype(np.uint8)
        _G[k] = Image.fromarray(arr, "RGB")
    return _G[k]

def sade(s):
    return s.strip()

# ---------------- cizimler ----------------
def hook_katman(acik):
    L = Image.new("RGBA", (W, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((200, 60, 880, 640), fill=(12, 16, 30), outline=(40, 50, 80), width=4)
    d.polygon([(180, 60), (540, 0), (900, 60)], fill=(20, 24, 44))
    for r in range(4):
        for c in range(4):
            x = 250 + c * 150; y = 110 + r * 135
            renk = (190, 130, 40) if (r + c) % 3 == 0 else (22, 30, 52)
            if r == 2 and c == 2: renk = (235, 40, 40) if acik else (110, 20, 24)
            d.rounded_rectangle((x, y, x + 100, y + 95), 10, fill=renk)
    return L

def ipucu_katman(renk):
    L = Image.new("RGBA", (W, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.ellipse((260, 20, 760, 520), fill=(10, 16, 36), outline=renk, width=28)
    d.line((700, 460, 820, 580), fill=renk, width=42)
    yaz(d, (510, 270), "?", 330, renk)
    return L

def kart_ciz(d, x0, i, ad, rol):
    c = RENK[i]
    d.rounded_rectangle((x0, 30, x0 + 300, 600), 30, fill=(16, 18, 38), outline=c, width=8)
    d.ellipse((x0 + 100, 70, x0 + 200, 170), fill=(60, 66, 100))
    d.pieslice((x0 + 60, 170, x0 + 240, 330), 180, 360, fill=(60, 66, 100))
    d.ellipse((x0 + 105, 290, x0 + 195, 380), fill=c)
    yaz(d, (x0 + 150, 335), HARF[i], 66, (255, 255, 255))
    yaz(d, (x0 + 150, 430), tr_upper(ad), 44 if len(ad) < 9 else 36, (255, 255, 255))
    t = textwrap.wrap(rol, 11)[:2]
    for n, s in enumerate(t):
        yaz(d, (x0 + 150, 500 + n * 40), s, 30, (200, 205, 235))

def supheli_katman(sup, kac):
    L = Image.new("RGBA", (W, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for i in range(kac):
        kart_ciz(d, 40 + i * 345, i, sup[i]["ad"], sup[i]["rol"])
    return L

def oy_katman(onceki, parla):
    L = Image.new("RGBA", (W, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for i in range(3):
        cx = 190 + i * 350
        r = 130 if parla == i else 118
        d.ellipse((cx - r, 150 - r, cx + r, 150 + r), fill=RENK[i], outline=(255, 255, 255), width=8)
        yaz(d, (cx, 150), HARF[i], 150, (255, 255, 255))
    yaz(d, (540, 360), "YORUMA HARFİNİ YAZ", 58, (255, 235, 110), stroke=6)
    if onceki:
        d.rounded_rectangle((60, 430, 1020, 620), 28, fill=(16, 20, 44), outline=(245, 200, 60), width=6)
        yaz(d, (540, 480), "DÜNKÜ KATİL", 34, (245, 200, 60))
        yaz(d, (540, 555), tr_upper(onceki), 76, (255, 255, 255), stroke=0)
    return L

# ---------------- ses efektleri ----------------
def ton(f, s, vol=.5, ck=6):
    t = np.arange(int(SR * s)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-ck * t) * vol
def sfx_hit():
    t = np.arange(int(SR * .8)) / SR
    n = np.random.RandomState(3).randn(len(t)) * np.exp(-14 * t) * .35
    return ton(55, .8, .9, 4.5) + n
def sfx_ding():
    return np.concatenate([ton(880, .12, .45, 5), ton(1175, .5, .45, 5)])
def sfx_pop():
    return np.concatenate([ton(520, .08, .5, 25), ton(780, .1, .4, 20)])
def sfx_whoosh():
    n = np.convolve(np.random.RandomState(2).randn(int(SR * .35)), np.ones(60) / 60, "same")
    return n * np.sin(np.linspace(0, np.pi, len(n))) ** 2 * 1.8
def sfx_tick():
    return ton(1500, .04, .5, 60)

def drone(sn):
    t = np.arange(int(SR * sn)) / SR
    trem = 0.7 + 0.3 * np.sin(2 * np.pi * 0.25 * t)
    return (np.sin(2 * np.pi * 55 * t) * .6 + np.sin(2 * np.pi * 82.4 * t) * .4) * trem * .05

# ---------------- vaka -> sahneler ----------------
def sahneler_yap(v, no, onceki):
    sup = v["supheliler"]
    anl3 = "Şüpheliler. " + " ".join(f"{HARF[i]}, {s['ad']}, {s['rol']}." for i, s in enumerate(sup))
    oy = "Katil kim? Harfini yoruma yaz!"
    if onceki:
        oy += f" Dünkü vakada katil {onceki} çıktı. Yarın yeni vaka!"
    else:
        oy += " Cevabı yarın açıklıyorum!"
    return [
        {"tip": "hook", "z": "hook", "baslik": v["baslik"], "anlatim": v["olay"]},
        {"tip": "ipucu", "z": "ipucu", "baslik": "İPUCU 1", "anlatim": v["ipuclari"][0], "renk": (245, 200, 60)},
        {"tip": "ipucu", "z": "ipucu2", "baslik": "İPUCU 2", "anlatim": v["ipuclari"][1], "renk": (90, 220, 240)},
        {"tip": "supheli", "z": "supheli", "baslik": "ŞÜPHELİLER", "anlatim": anl3, "sup": sup},
        {"tip": "oy", "z": "oy", "baslik": "KATİL KİM?", "anlatim": oy, "onceki": onceki},
    ]

def kelime_gruplari(metin):
    gr = []; cur = []
    for w in metin.split():
        if cur and (len("".join(cur)) + len(w) > 15 or len(cur) >= 3):
            gr.append(cur); cur = []
        cur.append(w)
        if w[-1] in ".?!,": gr.append(cur); cur = []
    if cur: gr.append(cur)
    return [" ".join(g) for g in gr]

def zamanla(metin, dur):
    gr = kelime_gruplari(metin)
    if not gr: return []
    agr = [len(g) + 3 + (6 if g[-1] in ".?!" else 2 if g[-1] == "," else 0) for g in gr]
    top = sum(agr); t = 0.05; out = []
    for g, a in zip(gr, agr):
        l = (dur - 0.15) * a / top
        out.append((t, t + l, tr_upper(g))); t += l
    return out

def katmanlar(sc):
    if sc["tip"] == "hook": return [hook_katman(True), hook_katman(False)]
    if sc["tip"] == "ipucu": return [ipucu_katman(sc["renk"])]
    if sc["tip"] == "supheli": return [supheli_katman(sc["sup"], k) for k in (1, 2, 3)]
    return [oy_katman(sc["onceki"], p) for p in (-1, 0, 1, 2)]

def katman_sec(s, lt):
    tip = s["sc"]["tip"]; n = len(s["kat"])
    if tip == "hook": return int(lt * 3) % 2
    if tip == "supheli": return min(n - 1, int(lt / (s["dur"] * .8) * 3))
    if tip == "oy": return min(n - 1, int(lt * 1.2) % 4)
    return 0

def plan(sahneler, sureler):
    out = []; bas = 0.0
    for sc, dur in zip(sahneler, sureler):
        out.append({"sc": sc, "bas": bas, "dur": dur, "kat": katmanlar(sc), "cap": zamanla(sc["anlatim"], dur)})
        bas += dur
    return out, bas

_C = {}
def chunk_resim(t):
    if t not in _C:
        sz = 108
        while font(sz).getlength(t) > 960 and sz > 40: sz -= 4
        im = Image.new("RGBA", (1040, 200), (0, 0, 0, 0))
        yaz(ImageDraw.Draw(im), (520, 100), t, sz, (255, 228, 60), stroke=11)
        _C[t] = im
    return _C[t]

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def kare(no, sah, toplam, t):
    i = 0
    for k, s in enumerate(sah):
        if s["bas"] <= t: i = k
    s = sah[i]; sc = s["sc"]; lt = t - s["bas"]
    img = zemin(sc["z"]).copy(); d = ImageDraw.Draw(img)
    kat = s["kat"][katman_sec(s, lt)]
    z = 1 + 0.07 * (lt / s["dur"])
    cw, ch = W / z, LH / z
    kes = kat.crop((int((W - cw) / 2), int((LH - ch) / 2), int((W + cw) / 2), int((LH + ch) / 2))).resize((W, LH), Image.BILINEAR)
    img.paste(kes, (0, int(LY + 80 * (1 - ease(lt / .2))) if lt < .2 else LY), kes)
    d.rounded_rectangle((30, 40, 1050, 200), 36, fill=(12, 8, 18), outline=(220, 40, 50), width=5)
    yaz(d, (70, 100), "MANŞET DEDEKTİF", 48, (240, 70, 70), "lm")
    yaz(d, (70, 155), "GİZEMLİ VAKA SERİSİ", 28, (190, 195, 225), "lm")
    d.rounded_rectangle((760, 70, 1010, 170), 24, fill=(220, 40, 50))
    yaz(d, (885, 120), f"DOSYA #{no:02d}", 42, (255, 255, 255))
    bs = textwrap.wrap(tr_upper(sc["baslik"]), 16)[:2]
    for n, satir in enumerate(bs):
        yaz(d, (540, 300 + n * 100 - (len(bs) - 1) * 40), satir, 92, (255, 255, 255), stroke=9)
    for a, b, tx in s["cap"]:
        if a <= lt < b:
            im = chunk_resim(tx); p = ease((lt - a) / .09); sc3 = .8 + .2 * p
            if sc3 < .999: im = im.resize((int(im.width * sc3), int(im.height * sc3)), Image.BILINEAR)
            img.paste(im, (540 - im.width // 2, 1370 - im.height // 2), im)
            break
    d.rectangle((0, 1790, int(W * t / toplam), 1802), fill=(240, 70, 70))
    yaz(d, (540, 1850), "t.me/manset_dedektif_bot/dedektif  ·  kurgusal vaka", 30, (225, 228, 245))
    return img

# ---------------- ses ----------------
def wav_oku(yol):
    with wave.open(yol, "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

def yaz_wav(yol, a):
    a = np.clip(a, -1, 1)
    with wave.open(yol, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())

async def tts(metin, mp3):
    import edge_tts
    await edge_tts.Communicate(metin, "tr-TR-AhmetNeural", rate="+10%", pitch="-4Hz").save(mp3)

def ses_uret(i, metin):
    wav = f"tmp{i}.wav"
    if os.environ.get("SAHTE_SES"):
        yaz_wav(wav, ton(220, max(1, len(metin.split())) * 0.36, .2, 0.1)); return wav_oku(wav)
    mp3 = f"tmp{i}.mp3"
    asyncio.run(tts(metin, mp3))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", str(SR), "-ac", "1", wav], check=True)
    return wav_oku(wav)

def karisim(sah, toplam, sesler):
    buf = np.zeros(int(SR * (toplam + 1)), dtype=np.float32)
    def ekle(x, sn, v=1.0):
        a = int(sn * SR); x = np.asarray(x, dtype=np.float32)[:max(0, len(buf) - a)] * v
        buf[a:a + len(x)] += x
    ekle(drone(toplam + .5), 0, 1.0)
    for n, (s, ses) in enumerate(zip(sah, sesler)):
        pk = np.max(np.abs(ses)) or 1
        ekle(ses / pk * .9, s["bas"] + .05)
        tip = s["sc"]["tip"]
        if n == 0: ekle(sfx_hit(), 0.0, .8)
        else: ekle(sfx_whoosh(), s["bas"], .15)
        if tip == "ipucu": ekle(sfx_ding(), s["bas"] + .1, .6)
        if tip == "supheli":
            for k in range(3): ekle(sfx_pop(), s["bas"] + k * s["dur"] * .8 / 3, .6)
        if tip == "oy":
            for k in range(3): ekle(sfx_tick(), s["bas"] + s["dur"] - 1.2 + k * .35, .5)
    return buf

def temiz_ad(c):
    s = c.strip()
    return s

def telegram(video, baslik, no, cozum):
    tok = os.environ.get("TELEGRAM_BOT_TOKEN"); chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not (tok and chat):
        print("Telegram bilgisi yok, gönderilmedi"); return
    ac = (f"Dosya #{no:02d}: {baslik}\n\n"
          f"Yarınki videoda söyleyeceğin cevap:\n{cozum}\n\n"
          "#dedektif #gizem #vaka #kurgusalhikaye")
    with open(video, "rb") as f:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendVideo",
                          data={"chat_id": chat, "caption": ac[:1000]}, files={"video": f})
    print("Telegram:", r.status_code, r.text[:200])

def main():
    vakalar = json.load(open("vakalar_v2.json", encoding="utf-8"))
    durum = json.load(open("state.json", encoding="utf-8")) if os.path.exists("state.json") else {}
    secili = (os.environ.get("VAKA_NO") or "").strip()
    idx = (int(secili) - 1) if secili.isdigit() else durum.get("v2_index", 0)
    idx %= len(vakalar)
    v = vakalar[idx]; no = idx + 1
    onceki = vakalar[idx - 1]["supheliler"][vakalar[idx - 1]["dogru"]]["ad"] if idx > 0 else None
    print("Vaka:", no, v["baslik"])
    sahneler = sahneler_yap(v, no, onceki)
    sesler = []; sureler = []
    for i, sc in enumerate(sahneler):
        a = ses_uret(i, sc["anlatim"])
        sesler.append(a); sureler.append(len(a) / SR + (.25 if i == 0 else .35))
    sah, top = plan(sahneler, sureler)
    yaz_wav("ses.wav", karisim(sah, top, sesler))
    kare(no, sah, top, 1.0).save("kapak.png")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "ses.wav",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-t", f"{top:.2f}", "-movflags", "+faststart",
                          "gunun_vakasi.mp4"], stdin=subprocess.PIPE)
    for n in range(int(top * FPS)):
        p.stdin.write(kare(no, sah, top, n / FPS).tobytes())
    p.stdin.close(); p.wait()
    print("Video hazır:", round(top, 1), "sn")
    telegram("gunun_vakasi.mp4", v["baslik"], no, v["cozum"])
    if not secili.isdigit():
        durum["v2_index"] = idx + 1
        json.dump(durum, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
