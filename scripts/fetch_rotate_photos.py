"""Baixa fotos livres do Wikimedia Commons para o captcha de "girar a imagem".

Uso: python scripts/fetch_rotate_photos.py
Cada foto é cortada em quadrado, reduzida e salva em assets/captcha/rotate/. O jogo as pixela com um
filtro mais leve que o dos gatinhos (ver src/minigames/common.py: load_rotate_photos), porque aqui a
pessoa precisa reconhecer o objeto rápido para saber girar.
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
OUT = ROOT / "assets" / "captcha" / "rotate"
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "SobAnalise-school-project/1.0 (educational game; contact gabrieldanielabreu@gmail.com)"}
FREE = re.compile(r"^(cc0|public domain|pd|cc[- ]by(-sa)?[- ]\d|cc by|cc-by)", re.I)

# name -> (search term, vertical crop center as a fraction of the height: 0.5 = middle)
SUBJECTS = {
    "person": ("person standing full body studio photo white background", 0.5),
    "bottle": ("glass bottle photo white background", 0.5),
    "chair": ("wooden chair photo white background", 0.5),
    "lamp": ("table lamp photo white background", 0.5),
    "cactus": ("cactus in pot photo white background", 0.5),
    "umbrella": ("open umbrella photo white background", 0.45),
    "guitar": ("acoustic guitar photo white background", 0.5),
    "kettle": ("tea kettle photo white background", 0.5),
}


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read()


def search(term: str) -> list[dict]:
    params = {
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
        "gsrsearch": f"{term} filetype:bitmap", "gsrlimit": "20", "prop": "imageinfo",
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
        if info.get("width", 0) < 350 or info.get("height", 0) < 350 or page["title"] in used:
            continue
        try:
            image = Image.open(io.BytesIO(get(info["thumburl"]))).convert("RGB")
        except Exception:
            continue
        used.add(page["title"])
        credit = {
            "title": page["title"], "author": strip_html(meta.get("Artist", {}).get("value", "")) or "desconhecido",
            "license": license_name, "url": info.get("descriptionurl", ""),
        }
        return image, credit
    return None


def square(image: Image.Image, center_y: float, size: int = 256) -> Image.Image:
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = max(0, min(height - side, round(height * center_y - side / 2)))
    return image.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    used: set[str] = set()
    credits: list[str] = []
    for name, (term, center_y) in SUBJECTS.items():
        found = pick(term, used)
        time.sleep(0.5)
        if found is None:
            print(f"FALHOU: {name} ({term})")
            continue
        image, credit = found
        square(image, center_y).save(OUT / f"{name}.jpg", quality=88)
        credits.append(f"| {name}.jpg | {credit['title'][5:]} | {credit['author'][:80]} | {credit['license']} | {credit['url']} |")
        print("ok", name, credit["title"], credit["license"])
    header = (
        "# Créditos das fotos do captcha de girar\n\nFotos do Wikimedia Commons (licenças livres). "
        "Recortadas em quadrado e pixeladas (filtro leve) no jogo.\n\n"
        "| Arquivo | Título | Autor | Licença | Página |\n|---|---|---|---|---|\n"
    )
    (OUT / "CREDITOS.md").write_text(header + "\n".join(credits) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
