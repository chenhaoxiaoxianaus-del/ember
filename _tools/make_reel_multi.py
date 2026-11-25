# usage: python3 make_reel_multi.py out.mp4 "DD MON YYYY" <theme> "<top text>" img1 img2 [img3 img4 ...]
import sys, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from render import THEMES
out, date_txt, theme, top_txt = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
srcs = [Image.open(p).convert("RGB") for p in sys.argv[5:]]
th = THEMES[theme % len(THEMES)]
hx = lambda h: tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
W, H, FPS, DUR = 1080, 1920, 30, 16.0
DEEP, ACC, CREAM = hx(th["deep"]), hx(th["accent"]), (244,241,232)
serif = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"; sans = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
f_top = ImageFont.truetype(serif, 62, index=3); f_kick = ImageFont.truetype(sans, 30, index=3)
f_bot = ImageFont.truetype(serif, 44, index=3); f_bot2 = ImageFont.truetype(sans, 28, index=3)
f_pg = ImageFont.truetype(sans, 26, index=3)
base = Image.new("RGB", (W, H), DEEP); d = ImageDraw.Draw(base)
def ctext(dr, y, s, f, fill):
    w = dr.textlength(s, font=f); dr.text(((W-w)/2, y), s, font=f, fill=fill)
ctext(d, 70, f"{th['kicker']} · {date_txt}", f_kick, ACC)
ctext(d, 118, top_txt, f_top, CREAM)
d.rectangle([(W/2-40, 222), (W/2+40, 226)], fill=ACC)
ctext(d, 1772, "關注「澳洲Ivan帶你看房」", f_bot, CREAM)
ctext(d, 1840, "每日精選澳洲新聞 · 地產 · 移民 · 生活", f_bot2, ACC)
n = len(srcs); seg = DUR / n; XF = 0.45
CARD_W = 1000; CARD_TOP, CARD_BOT = 262, 1700
def ease(t): return 0.5 - 0.5*math.cos(math.pi*max(0, min(1, t)))
def card(i, t):
    s = srcs[i]; sc = 0.95 + 0.05*ease(t/seg)
    cw = int(CARD_W*sc); ch = int(cw*s.size[1]/s.size[0])
    return s.resize((cw, ch), Image.BILINEAR), cw, ch
def frame_for(i, t):
    f = base.copy(); im, cw, ch = card(i, t)
    f.paste(im, ((W-cw)//2, int(CARD_TOP + (CARD_BOT-CARD_TOP-ch)/2)))
    dr = ImageDraw.Draw(f)
    # progress dots
    for k in range(n):
        x = W/2 - (n-1)*18 + k*36
        dr.ellipse([x-7, 1735-7, x+7, 1735+7], fill=ACC if k == i else (90,100,105))
    return f
p = subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
    "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-preset","veryfast","-crf","18",
    "-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-movflags","+faststart",out], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
for fi in range(int(DUR*FPS)):
    t = fi/FPS; i = min(n-1, int(t//seg)); lt = t - i*seg
    fr = frame_for(i, lt)
    if i < n-1 and lt > seg - XF:
        fr = Image.blend(fr, frame_for(i+1, 0), (lt-(seg-XF))/XF)
    if t < 0.5: fr = Image.blend(Image.new("RGB", (W, H), DEEP), fr, t/0.5)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait(); print("done", p.returncode)
