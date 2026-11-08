"""Lädt alle Tally-Bilder in den Vorschau-Seiten herunter und ersetzt die Links durch lokale Dateien."""
import html, pathlib, re, urllib.request

ROOT = pathlib.Path("vorschau")
PATTERN = re.compile(r'https://storage\.tally\.so/private/[^"\'\s<>)]+')
changed = False

for page in ROOT.glob("*/index.html"):
    text = page.read_text(encoding="utf-8")
    urls = sorted(set(PATTERN.findall(text)))
    if not urls:
        continue
    img_dir = page.parent / "img"
    img_dir.mkdir(exist_ok=True)
    for i, raw in enumerate(urls, 1):
        url = html.unescape(raw)
        name = url.split("/private/", 1)[1].split("?", 1)[0]
        name = re.sub(r"[^A-Za-z0-9._-]", "-", name) or f"bild-{i}.png"
        target = img_dir / name
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "webblitz-bilder"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
        except Exception as e:  # Bild bleibt als Link, nächster Lauf versucht es erneut
            print(f"FEHLER {page}: {name}: {e}")
            continue
        target.write_bytes(data)
        text = text.replace(raw, f"img/{name}")
        print(f"OK {page}: img/{name} ({len(data)} Bytes)")
    page.write_text(text, encoding="utf-8")
    changed = True

print("geaendert" if changed else "nichts zu tun")
