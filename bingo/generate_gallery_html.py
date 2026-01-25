#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import html
from collections import defaultdict

INCLUDE_ROOT_FILES = False
IMAGE_EXTS = {
    ".png", ".gif", ".jpg", ".jpeg", ".jfif", ".pjpeg", ".pjp", ".webp",
    ".svg", ".ico", ".bmp", ".dib", ".tif", ".tiff", ".heif", ".heic"
}
OUTPUT_HTML = "gallery.html"


def collect_images(base_dir: Path) -> list[Path]:
    base_dir = base_dir.resolve()
    images = []
    for root, dirs, files in os.walk(base_dir):
        root_path = Path(root)
        if not INCLUDE_ROOT_FILES and root_path == base_dir:
            continue
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in IMAGE_EXTS:
                images.append(root_path / f)
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
    .index { position:sticky; top:0; background:var(--bg); padding:8px 0 12px; border-bottom:1px solid var(--card-border); z-index:10; }
    .index a { display:inline-block; margin:6px 10px 0 0; padding:6px 10px; font-size:13px; color:var(--fg); text-decoration:none; background:var(--card-bg); border:1px solid var(--card-border); border-radius:999px; box-shadow:0 1px 4px rgba(0,0,0,.04); }
    .index a:hover { background:#f3f3f3; }
    .section { margin: 24px 0 40px; }
.section-title { 
  margin: 0 0 12px; 
  font-size: 32px; 
  font-weight: 900; 
  letter-spacing: -.02em; 
  border-left: 8px solid var(--card-border); 
  padding-left: 14px; 
  line-height: 1.15; 
}
    .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:16px; }
    .figure { display:flex; flex-direction:column; align-items:center; }
    .figure a { display:block; width:100%; background:var(--card-bg); border:1px solid var(--card-border);
      border-radius:12px; overflow:hidden; box-shadow:0 4px 16px rgba(0,0,0,.06); text-decoration:none; }
    .figure img { display:block; width:100%; height:auto; }
    .caption { margin-top:8px; color:var(--muted); font-size:13px; text-align:center; word-break:break-all; }
  </style>
</head>
<body>
  <div class=\"container\">\n    <header>\n      <h1>Afbeeldingen galerij</h1>\n"""
    tail = """    </header>
  </div>
</body>
</html>
"""

    import re

    def make_anchor_id(name: str) -> str:
        s = name.strip().lower().replace(' ', '-')
        s = re.sub(r'[^a-z0-9\-_.]', '', s)
        return s or 'sectie'

    groups: dict[str, list[Path]] = defaultdict(list)
    for img_path in images:
        rel = img_path.relative_to(base_dir)
        parts = rel.parts
        group = "(Hoofdmap)"
        if len(parts) >= 2 and parts[0].lower() in ("stedenendorpen", "dorpenensteden"):
            # Path like: stedenendorpen|dorpenensteden/StapX/...
            group = parts[1]
        elif len(parts) >= 1:
            # Path like: StapX/...
            group = parts[0]
        groups[group].append(img_path)

    parts_out: list[str] = [head]

    total_count = len(images)
    parts_out.append(f"      <p>Alle afbeeldingen uit submappen (klik om te openen). Bijschrift toont het relatieve pad. Totaal: {total_count} foto's.</p>\n")
    parts_out.append(f"      <p>Root: {html.escape(str(base_dir))}</p>\n")

    group_names = sorted(groups.keys(), key=lambda s: s.lower())
    index_html = "    <nav class=\"index\">\n      " + "\n      ".join([
        f"<a href=\"#{make_anchor_id(name)}\">Stap: {html.escape(name)}</a>" for name in group_names
    ]) + "\n    </nav>\n"
    parts_out.append(index_html)

    html_dir = Path(__file__).parent.resolve()

    for group_name in group_names:
        safe_group = html.escape(group_name)
        group_images = sorted(groups[group_name], key=lambda p: str(p.relative_to(base_dir)).lower())
        count = len(group_images)
        anchor = make_anchor_id(group_name)
        parts_out.append(f"    <section class=\"section\" id=\"{anchor}\">\n      <h1 class=\"section-title\">Stap: {safe_group} ({count})</h1>\n      <div class=\"grid\">\n")
        for img_path in group_images:
            rel = img_path.relative_to(base_dir)
            rel_str = str(rel).replace("\\", "/")
            safe_rel = html.escape(rel_str)
            link_rel = os.path.relpath(str(img_path), start=str(html_dir))
            link_rel = link_rel.replace("\\", "/")
            safe_link = html.escape(link_rel)
            block = f"""        <div class=\"figure\">\n          <a href=\"{safe_link}\" target=\"_blank\" rel=\"noopener\">\n            <img src=\"{safe_link}\" alt=\"{safe_rel}\">\n          </a>\n          <div class=\"caption\">{safe_rel}</div>\n        </div>\n"""
            parts_out.append(block)
        parts_out.append("      </div>\n    </section>\n")

    parts_out.append(tail)
    return "".join(parts_out)

def main():
    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1])
    else:
        base_dir = Path(__file__).parent
    base_dir = base_dir.resolve()

    images = collect_images(base_dir)

    if not images:
        print("Geen afbeeldingen gevonden in map:", base_dir)
        sys.exit(1)

    html_content = build_html(base_dir, images)

    # Write gallery.html to the same folder as the script
    html_dir = Path(__file__).parent.resolve()
    output_path = html_dir / OUTPUT_HTML
    output_path.write_text(html_content, encoding='utf-8')
    print(f"HTML galerij gemaakt: {output_path}")


if __name__ == "__main__":
    main()

