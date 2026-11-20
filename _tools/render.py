import base64, json, sys, pathlib, asyncio, io
import qrcode
from jinja2 import Template
from playwright.async_api import async_playwright
HERE = pathlib.Path(__file__).parent
THEMES = [
 {"name":"深青","deep":"#06313f","accent":"#16b3b3","accent_text":"#0f8f8f","bg":"#f4f1e8","line":"#d9d4c6","kicker":"DAILY BRIEFING"},
 {"name":"海軍藍金","deep":"#14213d","accent":"#e0a526","accent_text":"#a87710","bg":"#f6f3ec","line":"#ddd5c3","kicker":"AUSTRALIA TODAY"},
 {"name":"墨綠","deep":"#16362b","accent":"#4fbf8b","accent_text":"#2e8a5f","bg":"#f2f2ea","line":"#d6d8c8","kicker":"MARKET MORNING"},
 {"name":"酒紅","deep":"#4a1626","accent":"#e07a5f","accent_text":"#b5523a","bg":"#f7f1ec","line":"#e1d3c9","kicker":"DAILY BRIEFING"},
 {"name":"石墨橙","deep":"#1f2a33","accent":"#f08a24","accent_text":"#c0650a","bg":"#f3f3f0","line":"#d8d8d2","kicker":"THE AUSSIE DAILY"},
 {"name":"皇家藍","deep":"#0f2d5c","accent":"#3fa7f5","accent_text":"#1b6fb0","bg":"#f1f4f8","line":"#d3dbe6","kicker":"MORNING NOTES"},
 {"name":"紫灰","deep":"#2d2342","accent":"#b48ce0","accent_text":"#7a52a8","bg":"#f4f2f6","line":"#dcd6e3","kicker":"WEEKEND EDITION"},
]
FONT_DIR = HERE / "node_modules/@fontsource/manrope/files"
def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()
def qr_b64(fill="#06313f"):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=2)
    q.add_data("https://u.wechat.com/kE9GOba0Ii_mBlG-ZcXSgcU?s=2"); q.make(fit=True)
    buf = io.BytesIO(); q.make_image(fill_color=fill, back_color="white").save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()
def build(mode, data):
    H = 1527 if mode == "a4" else 1350
    fonts = {k: b64(FONT_DIR / f"manrope-latin-{w}-normal.woff2") for k, w in (("m600",600),("m700",700),("m800",800))}
    tpl = Template((HERE / "news_template.html").read_text(encoding="utf-8"))
    th = THEMES[int(data.get("theme", 0)) % len(THEMES)]
    return H, tpl.render(d=data, mode=mode, H=H, fonts=fonts, qr=qr_b64(th["deep"]), th=th)
async def main(data_path, out_dir):
    data = json.loads(pathlib.Path(data_path).read_text(encoding="utf-8"))
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for mode, name in (("a4", "news_A4.png"), ("ig", "news_IG_4x5.png")):
            H, html = build(mode, data)
            pg = await br.new_page(viewport={"width":1080,"height":H}, device_scale_factor=2)
            await pg.set_content(html, wait_until="networkidle"); await pg.evaluate("document.fonts.ready")
            await pg.screenshot(path=str(out / name)); await pg.close()
        await br.close()
if __name__ == "__main__": asyncio.run(main(sys.argv[1], sys.argv[2]))
