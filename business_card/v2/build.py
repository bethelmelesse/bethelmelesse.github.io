"""Build assets and PDFs for the V2 (formal) business card.

Generates:
  - IMG/parahigg-logo-back.png   logo recoloured white → light blue for the navy back
  - ../fonts/StandardSerif.ttf  TrueType copy of the serif (Chrome embeds the CFF .otf as Type 3, which printers dislike)
  - IMG/parahigg-qr.svg          QR code for https://parahigg.com
  - bethel-business-card-v2.pdf        90 × 50 mm, trim size (screen / home printing)
  - bethel-business-card-v2-print.pdf  96 × 56 mm, 3 mm bleed (send this one to the print shop)
  - preview.png
(IMG = asset/img/business_card, shared with the V1 card)

Run:
  uv run --no-project --with pillow --with numpy --with fonttools --with segno python build.py
"""
import subprocess
from pathlib import Path

import numpy as np
import segno
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from PIL import Image

HERE = Path(__file__).parent
FONTS = HERE.parent / "fonts"
IMG = HERE.parent.parent / "asset" / "img" / "business_card"
CHROME = ["google-chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--hide-scrollbars"]


def back_logo():
    """Map navy→white, light blue→#9cc0ea so the logo reads on navy but keeps its gradient."""
    img = np.array(Image.open(IMG / "parahigg-logo.png").convert("RGBA")).astype(float)
    lum = img[..., :3].mean(-1)
    t = np.clip((lum - 45) / (150 - 45), 0, 1)[..., None]
    white, blue = np.array([255, 255, 255]), np.array([156, 192, 234])
    img[..., :3] = white * (1 - t) + blue * t
    Image.fromarray(img.astype(np.uint8)).save(IMG / "parahigg-logo-back.png")


def serif_ttf():
    """Convert the CFF-based StandardSerif.otf to quadratic TrueType outlines."""
    font = TTFont(FONTS / "StandardSerif.otf")
    glyph_set = font.getGlyphSet()
    glyf = newTable("glyf")
    glyf.glyphOrder = font.getGlyphOrder()
    glyf.glyphs = {}
    for name in glyf.glyphOrder:
        pen = TTGlyphPen(glyph_set)
        glyph_set[name].draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=True))
        glyf.glyphs[name] = pen.glyph()
    font["glyf"] = glyf
    font["loca"] = newTable("loca")
    font["maxp"].tableVersion = 0x00010000
    for attr in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
                 "maxStackElements", "maxSizeOfInstructions", "maxComponentElements"):
        setattr(font["maxp"], attr, 0 if attr != "maxZones" else 1)
    font["maxp"].maxComponentDepth = 0
    font["head"].glyphDataFormat = 0
    font["post"].formatType = 2.0
    font["post"].extraNames = []
    font["post"].mapping = {}
    del font["CFF "]
    if "VORG" in font:
        del font["VORG"]
    font.sfntVersion = "\x00\x01\x00\x00"
    font.save(FONTS / "StandardSerif.ttf")


def pdfs():
    page = (HERE / "index.html").as_uri()
    subprocess.run(CHROME + ["--print-to-pdf=bethel-business-card-v2.pdf", page], cwd=HERE, check=True, capture_output=True)
    subprocess.run(CHROME + ["--print-to-pdf=bethel-business-card-v2-print.pdf", page + "?bleed"], cwd=HERE, check=True, capture_output=True)
    subprocess.run(CHROME + ["--window-size=1440,1000", "--screenshot=preview.png", page], cwd=HERE, check=True, capture_output=True)


if __name__ == "__main__":
    back_logo()
    serif_ttf()
    segno.make("https://parahigg.com", error="m").save(IMG / "parahigg-qr.svg", scale=1, border=4, xmldecl=True, svgclass=None)
    qr = (IMG / "parahigg-qr.svg").read_text()
    (IMG / "parahigg-qr.svg").write_text(qr.replace('width="33" height="33"', 'viewBox="0 0 33 33" width="33" height="33"', 1))
    pdfs()
