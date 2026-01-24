#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import html

# Config
# Set to True if you also want to include files directly in the root directory
INCLUDE_ROOT_FILES = False
# Image extensions to include
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
# Output HTML file name
OUTPUT_HTML = "gallery.html"

def collect_images(base_dir: Path) -> list[Path]:
    images = []
    base_dir = base_dir.resolve()
    for root, dirs, files in os.walk(base_dir):
        root_path = Path(root)
        # Skip files in root if not including root files
        for f in files:
            p = root_path / f
            if p.suffix.lower() in IMAGE_EXTS:
                if INCLUDE_ROOT_FILES or root_path != base_dir:
                    images.append(p)
                elif INCLUDE_ROOT_FILES:
                    images.append(p)
    # Sort by relative path
    images.sort(key=lambda p: str(p.relative_to(base_dir)).lower())
    return images

def build_html(base_dir: Path, images: list[Path]) -> str:
    head = """<!DOCTYPE html>
<html lang=\"nl\">
<head>
  <meta charset=\"utf-8\">
  <title>Galerij</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <style>
    :root { --bg:#fafafa; --fg:#1a1a1a; --muted:#666; --card-bg:#fff; --card-border:#eee; --maxw:1000px; }
    html,body { margin:0; padding:0; background:var(--bg); color:var(--fg);
      font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,\"Helvetica Neue\",Arial,system-ui,sans-serif;
      line-height:1.6; -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; }
    .container { max-width:var(--maxw); margin:0 auto; padding:24px 16px 64px; }
    header { margin:0 0 24px; padding:24px 0 8px; border-bottom:1px solid var(--card-border); }
    header h1 { margin:0 0 6px; font-size:28px; font-weight:700; letter-spacing:-.02em; }
    header p { margin:0; color:var(--muted); font-size:14px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:16px; }
    .figure { display:flex; flex-direction:column; align-items:center; }
    .figure a { display:block; width:100%; background:var(--card-bg); border:1px solid var(--card-border);
      border-radius:12px; overflow:hidden; box-shadow:0 4px 16px rgba(0,0,0,.06); text-decoration:none; }
    .figure img { display:block; width:100%; height:auto; }
    .caption { margin-top:8px; color:var(--muted); font-size:13px; text-align:center; word-break:break-all; }
  </style>
</head>
<body>
  <div class=\"container\">
    <header>
      <h1>Afbeeldingen galerij</h1>
      <p>Alle afbeeldingen uit submappen (klik om te openen). Bijschrift toont het relatieve pad.</p>
    </header>
    <div class=\"grid\">
"""
    tail = """    </div>
  </div>
</body>
</html>
"""
    parts = [head]
    for img_path in images:
        rel = img_path.relative_to(base_dir)
        rel_str = str(rel).replace("\\", "/")
        safe_rel = html.escape(rel_str)
        block = f"""      <div class=\"figure\">
        <a href=\"{safe_rel}\" target=\"_blank\" rel=\"noopener\">
          <img src=\"{safe_rel}\" alt=\"{safe_rel}\">
        </a>
        <div class=\"caption\">{safe_rel}</div>
      </div>
"""
        parts.append(block)
    parts.append(tail)
    return "".join(parts)

def main():
    # Base directory = directory of this script, or provided via CLI
    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1]).resolve()
    else:
        base_dir = Path(__file__).resolve().parent

    images = collect_images(base_dir)
    if not images:
        print("Geen afbeeldingen gevonden in subfolders.")
    html_str = build_html(base_dir, images)
    out_path = base_dir / OUTPUT_HTML
    out_path.write_text(html_str, encoding="utf-8")
    print(f"Galerij geschreven naar: {out_path}")

if __name__ == "__main__":
    main()
