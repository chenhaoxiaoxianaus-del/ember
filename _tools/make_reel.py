import sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont
import json
src = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]; date_txt = sys.argv[3]
theme = int(sys.argv[4]) if len(sys.argv) > 4 else 0
top_txt = sys.argv[5] if len(sys.argv) > 5 else "今日澳洲 三分鐘看懂"
sys.path.insert(0, __import__("os").path.dirname(__file__)); from render import THEMES
th = THEMES[theme % len(THEMES)]
hx = lambda h: tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
W, H, FPS, DUR = 1080, 1920, 30, 15.0
DEEP, TEAL, CREAM = hx(th["deep"]), hx(th["accent"]), (244,241,232)
serif = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"; sans = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
f_top = ImageFont.truetype(serif, 62, index=3); f_kick = ImageFont.truetype(sans, 30, index=3)
f_bot = ImageFont.truetype(serif, 44, index=3); f_bot2 = ImageFont.truetype(sans, 28, index=3)
base = Image.new("RGB", (W, H), DEEP); d = ImageDraw.Draw(base)
def ctext(y, s, f, fill):
    w = d.textlength(s, font=f); d.text(((W-w)/2, y), s, font=f, fill=fill)
ctext(70, f"{th['kicker']} · {date_txt}", f_kick, TEAL)
ctext(118, top_txt, f_top, CREAM)
d.rectangle([(W/2-40, 222), (W/2+40, 226)], fill=TEAL)
ctext(1752, "關注「澳洲Ivan帶你看房」", f_bot, CREAM)
ctext(1820, "每日更新 地產・經濟・移民 最新動態", f_bot2, TEAL)
CARD_W = 1000; CARD_TOP, CARD_BOT = 255, 1720
sw, sh = src.size
def ease(t): return 0.5 - 0.5*math.cos(math.pi*max(0, min(1, t)))
cache = {}
p = subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
    "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-preset","veryfast","-crf","18",
    "-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-movflags","+faststart",out], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
for i in range(int(DUR*FPS)):
    t = i/FPS
    s = 0.94 + 0.06*ease(t/DUR)
    fade = min(1, t/0.6)
    cw = int(CARD_W*s); ch = int(cw*sh/sw)
    if (cw, ch) not in cache: cache.clear(); cache[(cw, ch)] = src.resize((cw, ch), Image.LANCZOS)
    frame = base.copy()
    y = int(CARD_TOP + (CARD_BOT-CARD_TOP-ch)/2)
    frame.paste(cache[(cw, ch)], ((W-cw)//2, y))
    if fade < 1: frame = Image.blend(Image.new("RGB", (W, H), DEEP), frame, fade)
    p.stdin.write(frame.tobytes())
p.stdin.close(); p.wait(); print("done", p.returncode)
