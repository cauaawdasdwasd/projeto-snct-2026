"""Baixa fotos livres do Wikimedia Commons para os captchas e gera CREDITOS.md.

Uso: python scripts/fetch_captcha_photos.py
Cada foto é cortada em quadrado, reduzida para 256x256 e salva em assets/captcha/photos/.
Depois o jogo as pixela em tempo de execução (ver src/minigames/common.py: pixelate_photo).
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "captcha" / "tiles"
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "SobAnalise-school-project/1.0 (educational game; contact gabrieldanielabreu@gmail.com)"}
FREE = re.compile(r"^(cc0|public domain|pd|cc[- ]by(-sa)?[- ]\d|cc by|cc-by)", re.I)

CATS = [
    "orange tabby cat face",
    "gray cat portrait",
    "black cat portrait yellow eyes",
    "white cat blue eyes",
    "calico cat face",
    "siamese cat portrait",
    "tuxedo cat face",
    "kitten portrait",
]
OTHERS = [
    "shiba inu face",
    "red fox portrait",
    "owl face portrait",
    "coyote close up",
    "loaf of bread sliced",
    "goat head animal farm",
    "pug dog face",
    "sheep face portrait",
]


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read()


def search(term: str) -> list[dict]:
    params = {
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
        "gsrsearch": f"{term} filetype:bitmap", "gsrlimit": "25", "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime", "iiurlwidth": "480",
    }
    data = json.loads(get(f"{API}?{urllib.parse.urlencode(params)}"))
    pages = data.get("query", {}).get("pages", {})
    return sorted(pages.values(), key=lambda page: page.get("index", 0))


def strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text or "")).strip()


def pick(term: str, used: set[str]) -> tuple[Image.Image, dict] | None:
    for page in search(term):
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        license_name = strip_html(meta.get("LicenseShortName", {}).get("value", ""))
        if not FREE.match(license_name) or info.get("mime") not in ("image/jpeg", "image/png"):
            continue
        if info.get("width", 0) < 400 or info.get("height", 0) < 400 or page["title"] in used:
            continue
        try:
            image = Image.open(io.BytesIO(get(info["thumburl"]))).convert("RGB")
        except Exception:
            continue
        used.add(page["title"])
        credit = {
            "title": page["title"],
            "author": strip_html(meta.get("Artist", {}).get("value", "")) or "desconhecido",
            "license": license_name,
            "url": info.get("descriptionurl", ""),
        }
        return image, credit
    return None


def square(image: Image.Image, size: int = 256) -> Image.Image:
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = max(0, (height - side) // 3)  # faces costumam ficar na parte de cima
    return image.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    used: set[str] = set()
    credits: list[str] = []
    for prefix, terms in (("cat", CATS), ("other", OTHERS)):
        for index, term in enumerate(terms, 1):
            found = pick(term, used)
            time.sleep(0.5)
            if found is None:
                print(f"FALHOU: {term}")
                continue
            image, credit = found
            name = f"{prefix}_{index:02d}.jpg"
            square(image).save(OUT / name, quality=88)
            credits.append(f"| {name} | {credit['title'][5:]} | {credit['author'][:80]} | {credit['license']} | {credit['url']} |")
            print("ok", name, credit["title"], credit["license"])
    header = (
        "# Créditos das fotos dos captchas\n\nFotos do Wikimedia Commons (licenças livres). "
        "Recortadas em quadrado, reduzidas e pixeladas no jogo.\n\n"
        "| Arquivo | Título | Autor | Licença | Página |\n|---|---|---|---|---|\n"
    )
    (ROOT / "assets" / "captcha" / "CREDITOS.md").write_text(header + "\n".join(credits) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
