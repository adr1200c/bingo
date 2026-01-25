#!/usr/bin/env python3
import os
import re
import html
from pathlib import Path

# Pas BASE_DIR en OUTPUT aan als je een andere structuur gebruikt
ROOT = Path(__file__).parent
BASE_DIR = ROOT / "stedenendorpen"
OUTPUT = ROOT / "gallery.html"

# Eenvoudige regex-extractors voor title, h1 en p (basis, niet 100% waterdicht)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)

def extract_text(html_text: str):
    """Haal een titel (title of h1) en de eerste paragraaf op uit HTML."""
    title = None
    m = TITLE_RE.search(html_text)
    if m:
        title = clean_html_text(m.group(1))
    if not title:
        m = H1_RE.search(html_text)
        if m:
            title = clean_html_text(m.group(1))
    # eerste paragraaf
    desc = None
    m = P_RE.search(html_text)
    if m:
        desc = clean_html_text(m.group(1))
    return title or "Onbekende plaats", desc or "Geen beschrijving beschikbaar."

def clean_html_text(s: str) -> str:
    """Verwijder simpele tags en decodeer HTML-entiteiten."""
    s = re.sub(r"<[^>]+>", "", s)  # strip tags
    s = html.unescape(s).strip()
    return s

def generate_card(title: str, desc: str, rel_path: str) -> str:
    return f"""
        <article class=\"card\">\n          <h2><a href=\"{rel_path}\">{html.escape(title)}</a></h2>\n          <p>{html.escape(desc)}</p>\n        </article>
    """.strip()

def main():
    if not BASE_DIR.exists():
        print(f"Map niet gevonden: {BASE_DIR}")
        return

    cards = []

    for entry in sorted(BASE_DIR.iterdir()):
        if entry.is_dir():
            name = entry.name  # submapnaam, bijv. 'ermelo'
            candidate = entry / f"{name}.html"
            if candidate.exists():
                try:
                    text = candidate.read_text(encoding="utf-8", errors="ignore")
                except Exception as e:
                    print(f"Fout bij lezen van {candidate}: {e}")
                    continue

                title, desc = extract_text(text)
                rel_path = os.path.relpath(candidate, OUTPUT.parent)
                cards.append(generate_card(title, desc, rel_path))
            else:
                print(f"Geen HTML gevonden voor submap: {entry} (verwacht: {candidate.name})")

    html_doc = f"""<!DOCTYPE html>
<html lang=\"nl\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
  <title>Gallery: Steden & Dorpen</title>
  <style>
    :root {{
      --bg: #fafafa; --fg: #1a1a1a; --muted: #666; --accent: #1e88e5;
      --card-bg: #fff; --card-border: #eee; --maxw: 1100px;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--fg);
      font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, system-ui, sans-serif; line-height: 1.6; }}
    .container {{ max-width: var(--maxw); margin: 0 auto; padding: 24px 16px 64px; }}
    header {{ margin: 0 0 24px; padding: 24px 0 8px; border-bottom: 1px solid var(--card-border); }}
    header h1 {{ margin: 0 0 6px; font-size: 28px; font-weight: 700; letter-spacing: -0.02em; }}
    header p {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }}
    .card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 14px;
             box-shadow: 0 4px 16px rgba(0,0,0,.06); transition: transform .1s ease, box-shadow .2s ease; }}
    .card:hover {{ transform: translateY(-1px); box-shadow: 0 8px 24px rgba(0,0,0,.08); }}
    .card a {{ color: var(--accent); text-decoration: none; }}
    .card h2 {{ margin: 0 0 8px; font-size: 18px; line-height: 1.3; }}
    .card p {{ margin: 0; font-size: 14px; color: var(--muted); }}
    .footer {{ margin-top: 32px; color: var(--muted); font-size: 13px; text-align: center; }}
  </style>
</head>
<body>
  <div class=\"container\">
    <header>
      <h1>Steden & Dorpen</h1>
      <p>Beschrijvingen per plaats, automatisch samengevoegd.</p>
    </header>
    <main>
      <div class=\"gallery\">\n        {''.join(cards)}\n      </div>
    </main>
    <p class=\"footer\">Gegenereerd uit de submappen van stedenendorpen/</p>
  </div>
</body>
</html>"""

    OUTPUT.write_text(html_doc, encoding="utf-8")
    print(f"Gallery geschreven naar: {OUTPUT}")

if __name__ == "__main__":
    main()
