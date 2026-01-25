#!/usr/bin/env python3
import os
import sys
import argparse
from typing import List

HTML_HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang=\"nl\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{title}</title>
  <style>
    :root {{ --bg:#fafafa; --fg:#1a1a1a; --muted:#666; --accent:#1e88e5; --card-bg:#fff; --card-border:#eee; --maxw:900px; }}
    html,body{{margin:0;padding:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,\"Helvetica Neue\",Arial,system-ui,sans-serif;line-height:1.6}}
    .container{{max-width:var(--maxw);margin:0 auto;padding:24px 16px 64px}}
    header{{margin:0 0 24px;padding:24px 0 8px;border-bottom:1px solid var(--card-border)}}
    header h1{{margin:0 0 6px;font-size:28px;font-weight:700}}
    header p{{margin:0;color:var(--muted);font-size:14px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}
    .tile{{border:1px solid var(--card-border);border-radius:10px;overflow:hidden;background:var(--card-bg);box-shadow:0 2px 10px rgba(0,0,0,.04)}}
    .tile img{{display:block;width:100%;height:180px;object-fit:cover}}
    .tile .cap{{padding:8px 10px;font-size:12px;color:var(--muted)}}
    a{{color:var(--accent);text-decoration:none}}
    footer{{margin-top:32px;color:var(--muted);font-size:12px}}
    @media print{{ .tile{{box-shadow:none}} }}
  </style>
</head>
<body>
  <div class=\"container\">
    <header>
      <h1>{title}</h1>
      <p>{beschrijving}</p>
    </header>
    <main>
"""

HTML_TAIL = """
    </main>
    <footer>
      <p>Automatisch gegenereerd door generate_indexes.py.</p>
    </footer>
  </div>
</body>
</html>
"""

def collect_images(place_dir: str) -> List[str]:
    images: List[str] = []
    for root, dirs, files in os.walk(place_dir):
        for f in files:
            low = f.lower()
            if low.endswith((".png", ".jpg", ".jpeg", ".webp")):
                rel = os.path.relpath(os.path.join(root, f), place_dir)
                images.append(rel)
    images.sort()
    return images

def build_html(place_name: str, images: List[str], with_gallery: bool) -> str:
    plaatsnaam = place_name.replace('-', ' ').replace('_', ' ')
    title = f"{plaatsnaam.title()} — Fotoverslag"
    beschrijving = f"Welkom! Dit is een korte pagina over {plaatsnaam.title()}. Hieronder vind je een selectie afbeeldingen uit deze map."

    head = HTML_HEAD_TEMPLATE.format(title=title, beschrijving=beschrijving)
    body_parts: List[str] = []
    if with_gallery and images:
        body_parts.append("<section><div class=\"grid\">")
        for rel in images:
            cap = rel
            body_parts.append(
                "<div class=\"tile\">"
                + f"<a href=\"{rel}\" target=\"_blank\">"
                + f"<img src=\"{rel}\" alt=\"{cap}\"></a>"
                + f"<div class=\"cap\">{cap}</div>"
                + "</div>"
            )
        body_parts.append("</div></section>")
    else:
        body_parts.append("<p>Er zijn (nog) geen afbeeldingen of de galerij is uitgeschakeld.</p>")

    return head + "\n".join(body_parts) + HTML_TAIL


def main(argv=None):
    parser = argparse.ArgumentParser(description="Genereer index.html in elke submap van 'stedenendorpen'.")
    parser.add_argument('--base', type=str, default=None, help="Basismap (standaard: map van dit script)")
    parser.add_argument('--overwrite', action='store_true', help="Overschrijf bestaande index.html")
    parser.add_argument('--no-gallery', action='store_true', help="Schakel de afbeeldingsgalerij uit")
    args = parser.parse_args(argv)

    base_dir = args.base if args.base else os.path.dirname(os.path.abspath(__file__))
    steden_dir = os.path.join(base_dir, 'stedenendorpen')

    if not os.path.isdir(steden_dir):
        print("FOUT: Map 'stedenendorpen' niet gevonden in", base_dir)
        return 2

    created = 0
    updated = 0
    skipped = 0

    for name in sorted(os.listdir(steden_dir)):
        place_path = os.path.join(steden_dir, name)
        if not os.path.isdir(place_path):
            continue

        index_path = os.path.join(place_path, 'index.html')
        if os.path.exists(index_path) and not args.overwrite:
            skipped += 1
            continue

        images = collect_images(place_path)
        html_out = build_html(name, images, with_gallery=(not args.no_gallery))

        os.makedirs(place_path, exist_ok=True)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_out)

        if os.path.exists(index_path) and args.overwrite:
            # If file existed and we overwrote -> updated
            updated += 1
        elif not os.path.exists(index_path) or (not args.overwrite and not os.path.exists(index_path)):
            # If for some reason file doesn't exist (should not happen), count created
            created += 1
        else:
            # If file didn't exist before, count created
            created += 1

    print(f"Klaar. Aangemaakt: {created}, Bijgewerkt: {updated}, Overgeslagen: {skipped}.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
