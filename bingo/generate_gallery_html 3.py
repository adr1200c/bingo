#!/usr/bin/env python3
import os
import sys
import json
import argparse
from typing import Optional

HTML_HEAD = """<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ --bg:#fafafa; --fg:#1a1a1a; --muted:#666; --accent:#1e88e5; --card-bg:#fff; --card-border:#eee; --maxw:1100px; }}
    html,body{{margin:0;padding:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,\"Helvetica Neue\",Arial,system-ui,sans-serif;line-height:1.6}}
    .container{{max-width:var(--maxw);margin:0 auto;padding:24px 16px 64px}}
    header{{margin:0 0 24px;padding:24px 0 8px;border-bottom:1px solid var(--card-border)}}
    header h1{{margin:0 0 6px;font-size:28px;font-weight:700}}
    header p{{margin:0;color:var(--muted);font-size:14px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
    .card{{display:flex;flex-direction:column;border:1px solid var(--card-border);border-radius:12px;background:var(--card-bg);overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.05)}}
    .thumb img{{width:100%;height:180px;object-fit:cover;display:block;background:#ddd}}
    .content{{padding:10px 12px}}
    .content h3{{margin:0 0 6px;font-size:16px}}
    .content p{{margin:0;color:var(--muted);font-size:13px}}
    a.card-link{{text-decoration:none;color:inherit;display:block}}
    .no-thumb{{height:180px;background:linear-gradient(135deg,#e3f2fd,#bbdefb);display:flex;align-items:center;justify-content:center;color:#1e88e5;font-weight:600;font-size:18px}}
    footer{{margin-top:32px;color:var(--muted);font-size:12px}}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </header>
    <main>
      <div class="grid">
"""

HTML_TAIL = """
      </div>
    </main>
    <footer>
      <p>Automatisch gegenereerd door generate_gallery_html.py.</p>
    </footer>
  </div>
</body>
</html>
"""

def load_descriptions(base_dir: str) -> dict:
    path = os.path.join(base_dir, 'beschrijvingen.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}

IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.webp')

def first_image_in_folder(folder: str) -> Optional[str]:
    # Return a relative path to the first image found (depth-first), else None
    for root, dirs, files in os.walk(folder):
        for f in sorted(files):
            if f.lower().endswith(IMAGE_EXTS):
                return os.path.join(root, f)
    return None


def build_card_html(place_name: str, place_dir: str, base_dir: str, with_thumb: bool, descs: dict) -> str:
    plaatsnaam = place_name.replace('-', ' ').replace('_', ' ').title()
    index_path = os.path.join(place_dir, 'index.html')
    rel_index = os.path.relpath(index_path, base_dir)

    # Beschrijving
    custom = descs.get(place_name) or descs.get(plaatsnaam) or descs.get(place_name.title())
    if not custom:
        default_tpl = descs.get('_default')
        if isinstance(default_tpl, str):
            custom = default_tpl.replace('{plaats}', plaatsnaam)
    desc = custom if isinstance(custom, str) else ''

    # Thumbnail
    thumb_html = ''
    if with_thumb:
        first_img_abs = first_image_in_folder(place_dir)
        if first_img_abs:
            rel_img = os.path.relpath(first_img_abs, place_dir)
            # from gallery page location, link through the place folder
            rel_img_from_base = os.path.join(os.path.relpath(place_dir, base_dir), rel_img)
            thumb_html = f'<div class="thumb"><img src="{rel_img_from_base}" alt="{plaatsnaam}"></div>'
        else:
            thumb_html = f'<div class="no-thumb">{plaatsnaam}</div>'
    else:
        thumb_html = f'<div class="no-thumb">{plaatsnaam}</div>'

    return (
        f'<a class="card-link" href="{rel_index}" target="_blank">'
        f'  <div class="card">'
        f'    {thumb_html}'
        f'    <div class="content">'
        f'      <h3>{plaatsnaam}</h3>'
        f'      <p>{desc}</p>'
        f'    </div>'
        f'  </div>'
        f'</a>'
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description='Genereer een overzichtsgalerij met links naar plaats-indexpagina\'s.')
    parser.add_argument('--base', type=str, default=None, help='Basismap (standaard: map van dit script)')
    parser.add_argument('--output', type=str, default='stedenendorpen_galerij.html', help='Uitvoerbestand (HTML)')
    parser.add_argument('--no-thumbs', action='store_true', help='Genereer geen thumbnails')
    args = parser.parse_args(argv)

    base_dir = args.base if args.base else os.path.dirname(os.path.abspath(__file__))
    steden_dir = os.path.join(base_dir, 'stedenendorpen')

    if not os.path.isdir(steden_dir):
        print("FOUT: Map 'stedenendorpen' niet gevonden in", base_dir)
        return 2

    descs = load_descriptions(base_dir)

    places = [name for name in sorted(os.listdir(steden_dir)) if os.path.isdir(os.path.join(steden_dir, name))]
    if not places:
        print("Geen plaatsmappen gevonden onder 'stedenendorpen'.")

    title = 'Overzicht dorpen en steden'
    subtitle = 'Klik op een kaart om de indexpagina van het dorp of de stad te openen.'

    html = [HTML_HEAD.format(title=title, subtitle=subtitle)]

    for name in places:
        place_dir = os.path.join(steden_dir, name)
        card = build_card_html(name, place_dir, base_dir, with_thumb=(not args.no_thumbs), descs=descs)
        html.append(card)

    html.append(HTML_TAIL)
    out_path = os.path.join(base_dir, args.output)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(html))

    print(f"Galerij gegenereerd: {out_path}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
