import streamlit as st
import random
import os
import base64
from datetime import date

# 1. Pagina instellingen
st.set_page_config(page_title="Rietman Familie Bingo", layout="centered")

# 2. Verberg Streamlit rommel
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .block-container { padding-top: 1.5rem; }
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

st.title("📸 Rietman Familie Bingo")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = BASE_DIR

if not os.path.exists(IMAGE_DIR):
    st.error("Basismap niet gevonden.")
else:
    all_photos = []
    for root, dirs, files in os.walk(IMAGE_DIR):
        # Sla bestanden in de root (de map van bingo.py) zelf over; neem alleen subfolders mee
        if os.path.abspath(root) == os.path.abspath(IMAGE_DIR):
            continue
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                rel_path = os.path.relpath(os.path.join(root, f), IMAGE_DIR)
                all_photos.append(rel_path)
    all_photos = sorted(all_photos)

    # Geef voorrang aan submap 'stedenendorpen'
    priority_folder = os.path.join('stedenendorpen')
    priority_photos = [p for p in all_photos if p.split(os.sep)[0] == 'stedenendorpen']
    other_photos = [p for p in all_photos if p.split(os.sep)[0] != 'stedenendorpen']

    if len(all_photos) < 9:
        st.warning(f"Voeg minimaal 9 foto's toe.")
    else:
        # GEBRUIK EEN VASTE SEED OP BASIS VAN DE DATUM
        # Hierdoor krijgt iedereen vandaag dezelfde 9 foto's uit de map, 
        # ook na een refresh.
        today_seed = date.today().strftime("%Y%m%d")
        
        if 'my_cards' not in st.session_state:
            # We zetten de random generator even 'vast' op de datum van vandaag
            random.seed(today_seed)
            # Kies eerst uit prioritaire foto's, vul aan uit overige
            pri = priority_photos.copy()
            oth = other_photos.copy()
            random.shuffle(pri)
            random.shuffle(oth)
            combined = (pri + oth)[:max(9, 9)]
            if len(pri) >= 9:
                pool = pri
            else:
                pool = pri + oth
            if len(pool) < 9:
                st.warning("Onvoldoende afbeeldingen om 9 kaarten te vullen.")
                st.stop()
            selected_photos = pool[:9]
            # Schud ze daarna voor deze specifieke gebruiker (zodat niet iedereen dezelfde kaart heeft)
            random.seed()  # Zet random weer 'vrij'
            random.shuffle(selected_photos)
            st.session_state.my_cards = selected_photos

        paths = [os.path.join(BASE_DIR, name) for name in st.session_state.my_cards]
        b64_list = []
        for p in paths:
            b64 = get_base64_image(p)
            if b64:
                b64_list.append(b64)

        # Zoek naar een 'landkaart' afbeelding (bestandsnaam begint met 'landkaart')
        map_b64 = None
        try:
            # Zoek in de hoofdfolder (naast bingo.py) naar een bestand dat met 'landkaart' begint
            for fname in os.listdir(BASE_DIR):
                low = fname.lower()
                if low.startswith('landkaart') and low.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    map_path = os.path.join(BASE_DIR, fname)
                    map_b64 = get_base64_image(map_path)
                    break
        except Exception:
            map_b64 = None

        if not map_b64:
            st.warning("Landkaart niet gevonden. Plaats een bestand 'landkaart.jpg' (of .png/.jpeg/.webp) naast bingo.py.")

        overlay_style = ""
        if map_b64:
            overlay_style = f"background-image: url('data:image/jpeg;base64,{map_b64}');"
        
        html_code = f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
            <style>
                body {{ margin: 0; background: transparent; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }}
                #overlay {{
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: #ffffff; z-index: 100; display: flex; flex-direction: column;
                    justify-content: center; align-items: center; text-align: center;
                    background-size: cover; background-position: center; background-repeat: no-repeat;
                    backdrop-filter: none;
                }}
                .btn-container {{ display: flex; flex-direction: column; gap: 15px; width: 280px; }}
                .overlay-shade {{ background: rgba(255,255,255,0.6); padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }}
                .start-btn {{ padding: 20px; font-size: 18px; cursor: pointer; background: linear-gradient(135deg, #42a5f5, #1e88e5); color: white; border: none; border-radius: 15px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
                .start-btn.silent {{ background: #757575; }}
                
                #game-container {{ display: none; flex-direction: column; align-items: center; width: 95vw; max-width: 400px; }}
                .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; width: 100%; margin-bottom: 15px; }}
                .item {{ position: relative; aspect-ratio: 1/1; border-radius: 12px; overflow: hidden; border: 3px solid #fff; cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                img {{ width: 100%; height: 100%; object-fit: cover; pointer-events: none; }}
                
                .cross {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: none; pointer-events: none; z-index: 10; }}
                .cross::before, .cross::after {{ content: ''; position: absolute; top: 50%; left: 10%; width: 80%; height: 12px; background: rgba(230, 0, 0, 0.85); border-radius: 6px; }}
                .cross::before {{ transform: translateY(-50%) rotate(45deg); }}
                .cross::after {{ transform: translateY(-50%) rotate(-45deg); }}
                
                .selected .cross {{ display: block; }}
                .selected img {{ filter: grayscale(100%) brightness(0.4); }}
                
                .instruction {{ 
                    color: #333; font-size: 14px; text-align: center; background: #f0f2f6; 
                    padding: 12px; border-radius: 12px; border: 1px solid #ddd; line-height: 1.4;
                }}
            </style>
        </head>
        <body>
            <div id="overlay" style="{overlay_style}">
                <div class="overlay-shade">
                    <h3 style="color: #333; margin-bottom: 25px;">Rietman Familie Bingo</h3>
                    <div class="btn-container">
                        <button class="start-btn" onclick="startBingo(true)">Speel met Geluid 🔊</button>
                        <button class="start-btn silent" onclick="startBingo(false)">Stil Spelen 🔇</button>
                    </div>
                </div>
            </div>

            <div id="game-container">
                <div class="grid" id="bingoGrid">
                    {"".join([f'<div class="item" onclick="toggle(this, event)"><img src="data:image/jpeg;base64,{b}"><div class="cross"></div></div>' for b in b64_list])}
                </div>
                <div class="instruction">
                    🎁 1 rij = Bingo! | 🏅 2 rijen = Prijs | 🏆 Volle kaart = Hoofdprijs!
                </div>
            </div>

            <audio id="clickSound" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"></audio>
            <audio id="winSound" src="https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"></audio>

            <script>
                const clickSnd = document.getElementById('clickSound');
                const winSnd = document.getElementById('winSound');
                let soundEnabled = true;
                let winPhase = 0; 

                function startBingo(s) {{
                    soundEnabled = s;
                    if(s) {{ clickSnd.play().then(()=>{{clickSnd.pause();}}).catch(()=>{{" "}}); }}
                    document.getElementById('overlay').style.display = 'none';
                    document.getElementById('game-container').style.display = 'flex';
                }}

                function countFullLines() {{
                    const items = document.querySelectorAll('.item');
                    const selected = Array.from(items).map(el => el.classList.contains('selected'));
                    const winPatterns = [
                        [0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]
                    ];
                    let lines = 0;
                    winPatterns.forEach(p => {{ if(p.every(idx => selected[idx])) lines++; }});
                    return lines;
                }}

                function toggle(el, ev) {{
                    const isSel = !el.classList.contains('selected');
                    el.classList.toggle('selected');
                    
                    if(isSel) {{
                        if(soundEnabled) {{ clickSnd.currentTime=0; clickSnd.play(); }}
                        confetti({{ particleCount: 15, origin: {{ x: ev.clientX/window.innerWidth, y: ev.clientY/window.innerHeight }} }});
                    }}

                    const fullLines = countFullLines();
                    const totalSelected = document.querySelectorAll('.selected').length;

                    if(winPhase === 0 && fullLines >= 1) {{
                        winPhase = 1;
                        triggerWin("BINGO! Je hebt 1 RIJ vol! 🎁");
                    }} else if(winPhase === 1 && fullLines >= 2) {{
                        winPhase = 2;
                        triggerWin("BINGO! Je hebt 2 RIJEN vol! 🏅");
                    }} else if(winPhase === 2 && totalSelected === 9) {{
                        winPhase = 3;
                        if(soundEnabled) winSnd.play();
                        var end = Date.now() + 5000;
                        (function frame() {{
                            confetti({{ particleCount: 10, angle: 60, spread: 55, origin: {{ x: 0 }}, colors: ['#FFD700', '#FFFFFF'] }});
                            confetti({{ particleCount: 10, angle: 120, spread: 55, origin: {{ x: 1 }}, colors: ['#FFD700', '#FFFFFF'] }});
                            if (Date.now() < end) requestAnimationFrame(frame);
                        }}());
                        setTimeout(() => alert("HOOFDPRIJS!!! De hele kaart is vol! 🏆👑"), 1000);
                    }}
                }}

                function triggerWin(msg) {{
                    if(soundEnabled) winSnd.play();
                    confetti({{ particleCount: 100, spread: 70, origin: {{ y: 0.6 }} }});
                    setTimeout(() => alert(msg), 500);
                }}
            </script>
        </body>
        </html>
        """
        st.components.v1.html(html_code, height=640)

        st.divider()
        st.subheader("🖨️ Printbare kaarten genereren")
        num_cards = st.number_input("Aantal kaarten (1 per pagina)", min_value=1, max_value=200, value=35, step=1)
        if st.button("Genereer printbare kaarten"):
            # Helper: maak een functie om 9 foto's te kiezen volgens prioriteitslogica
            def pick_nine():
                # hergebruik dezelfde pri/oth lijsten
                local_pri = priority_photos.copy()
                local_oth = other_photos.copy()
                random.shuffle(local_pri)
                random.shuffle(local_oth)
                pool = local_pri if len(local_pri) >= 9 else (local_pri + local_oth)
                return pool[:9]
            # Bouw HTML voor printen: 1 kaart per pagina
            print_cards_html = """
            <html>
            <head>
                <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
                <style>
                    @page { size: A4; margin: 12mm; }
                    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; }
                    .card { padding: 6mm 0; page-break-before: always; page-break-after: always; break-before: page; break-after: page; break-inside: avoid; display: flex; flex-direction: column; align-items: center; }
                    .title { margin: 6px 0 10px; font-weight: 600; color: #333; }
                    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; width: 175mm; max-width: 100%; }
                    .cell { aspect-ratio: 1/1; border: 2px solid #000; border-radius: 6px; overflow: hidden; }
                    .cell img { width: 100%; height: 100%; object-fit: cover; }
                </style>
            </head>
            <body>
            """

            for i in range(int(num_cards)):
                selected = pick_nine()
                # Zet om naar base64
                imgs = []
                for rel in selected:
                    pth = os.path.join(BASE_DIR, rel)
                    b64 = get_base64_image(pth)
                    if b64:
                        imgs.append(b64)
                # Render kaart
                print_cards_html += f"<div class='card'><div class='title'>Kaart {i+1}</div><div class='grid'>" + \
                    "".join([f"<div class='cell'><img src='data:image/jpeg;base64,{b}'></div>" for b in imgs]) + \
                    "</div></div>"

            print_cards_html += "</body></html>"

            # Toon in de app
            st.components.v1.html(print_cards_html, height=900, scrolling=True)

            # Downloadknop voor HTML-bestand
            st.download_button(
                label="Download als HTML",
                data=print_cards_html.encode('utf-8'),
                file_name="print_kaarten.html",
                mime="text/html"
            )

        st.divider()
        st.markdown("---")

# Helper: check lines on a 3x3 card
def count_lines(selected_mask):
    # selected_mask is a list[9] of bool
    wins = 0
    lines = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in lines:
        if selected_mask[a] and selected_mask[b] and selected_mask[c]:
            wins += 1
    return wins

# -----------------------------
# Importeer verhaal.html (href-volgorde) en simuleer
# -----------------------------
st.divider()
st.subheader("📥 Importeer verhaal.html en simuleer")

uploaded_html = st.file_uploader("Upload verhaal.html (met <a href=...> naar echte fotopaden)", type=["html", "htm"], key="upload_verhaal_html")
if uploaded_html is not None:
    try:
        html_text = uploaded_html.read().decode('utf-8', errors='ignore')
        # Eenvoudige href-extractie uit <a ... href="...">
        import re
        hrefs = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', html_text, flags=re.IGNORECASE)
        st.write(f"Gevonden links: {len(hrefs)}")
        # Filter optioneel op paden die in de pool zitten
        pool = set(all_photos)
        valid_sequence = [h for h in hrefs if h in pool]
        invalid = [h for h in hrefs if h not in pool]
        with st.expander("Verhaalvolgorde (geldig)"):
            for v in valid_sequence:
                st.write(v)
        if invalid:
            with st.expander("Links niet in fotopool (worden genegeerd)"):
                for iv in invalid:
                    st.write(iv)
        if valid_sequence:
            # Controls for simulation
            num_players_html = st.number_input("Aantal spelers (HTML import)", min_value=1, max_value=500, value=35, step=1, key="players_html")
            day_pool_size = st.slider("Dagpool-grootte (meer overlap = hogere kans op 2 rijen/volle kaart)", min_value=9, max_value=30, value=15, step=1, help="De set waaruit alle kaarten worden samengesteld. Kleinere dagpool betekent dat kaarten meer items delen.")
            if st.button("Simuleer met geïmporteerde volgorde"):
                # Stel dagpool samen: eerst uit prioriteit, aanvullen met overige
                local_pri = priority_photos.copy()
                local_oth = other_photos.copy()
                random.shuffle(local_pri)
                random.shuffle(local_oth)
                day_pool = local_pri
                if len(day_pool) < day_pool_size:
                    day_pool += local_oth[:max(0, day_pool_size - len(day_pool))]
                day_pool = day_pool[:day_pool_size]
                # Genereer kaarten uit dagpool
                def make_card_from_daypool():
                    if len(day_pool) < 9:
                        return day_pool.copy()  # fallback
                    return random.sample(day_pool, 9)
                cards = [make_card_from_daypool() for _ in range(int(num_players_html))]

                selected_sets = [set() for _ in cards]
                results = []
                first_bingo_step = None
                first_bingo_count = 0

                # Per-card state to record first-time events
                has_one_line = [False] * len(cards)
                has_two_lines = [False] * len(cards)
                has_full = [False] * len(cards)
                events = []  # list of dicts with step, card, details

                def line_breakdown(mask):
                    rows = [(0,1,2),(3,4,5),(6,7,8)]
                    cols = [(0,3,6),(1,4,7),(2,5,8)]
                    diags = [(0,4,8),(2,4,6)]
                    h = sum(1 for a,b,c in rows if mask[a] and mask[b] and mask[c])
                    v = sum(1 for a,b,c in cols if mask[a] and mask[b] and mask[c])
                    d = sum(1 for a,b,c in diags if mask[a] and mask[b] and mask[c])
                    return {"h": h, "v": v, "d": d, "total": h+v+d}

                for step, item in enumerate(valid_sequence, start=1):
                    for idx, card in enumerate(cards):
                        if item in card:
                            selected_sets[idx].add(item)
                    one_line = two_lines = full_cards = 0
                    horiz_cards = vert_cards = diag_cards = 0
                    for idx, card in enumerate(cards):
                        mask = [c in selected_sets[idx] for c in card]
                        bd = line_breakdown(mask)
                        wins = bd["total"]

                        # Record new events (only first time they occur per card)
                        if not has_one_line[idx] and wins >= 1:
                            has_one_line[idx] = True
                            events.append({
                                "step": step,
                                "card": idx + 1,
                                "type": "1 rij",
                                "h": bd["h"], "v": bd["v"], "d": bd["d"], "total": wins,
                                "full": False
                            })
                        if not has_two_lines[idx] and wins >= 2:
                            has_two_lines[idx] = True
                            events.append({
                                "step": step,
                                "card": idx + 1,
                                "type": "2 rijen",
                                "h": bd["h"], "v": bd["v"], "d": bd["d"], "total": wins,
                                "full": False
                            })
                        if not has_full[idx] and all(mask):
                            has_full[idx] = True
                            events.append({
                                "step": step,
                                "card": idx + 1,
                                "type": "Volle kaart",
                                "h": bd["h"], "v": bd["v"], "d": bd["d"], "total": wins,
                                "full": True
                            })

                        if bd["h"] >= 1:
                            horiz_cards += 1
                        if bd["v"] >= 1:
                            vert_cards += 1
                        if bd["d"] >= 1:
                            diag_cards += 1
                        if wins >= 1:
                            one_line += 1
                        if wins >= 2:
                            two_lines += 1
                        if all(mask):
                            full_cards += 1
                    results.append({
                        "step": step,
                        "horiz": horiz_cards,
                        "vert": vert_cards,
                        "diag": diag_cards,
                        "one_line": one_line,
                        "two_lines": two_lines,
                        "full": full_cards
                    })
                    if first_bingo_step is None and one_line > 0:
                        first_bingo_step = step
                        first_bingo_count = one_line

                st.write("Resultaten per stap (HTML import):")
                for r in results:
                    st.write(
                        f"Stap {r['step']}: Horizontaal = {r['horiz']}, Verticaal = {r['vert']}, Diagonaal = {r['diag']}, "
                        f"1 rij = {r['one_line']}, 2 rijen = {r['two_lines']}, volle kaart = {r['full']}"
                    )
                if first_bingo_step is not None:
                    st.success(f"Eerste bingo valt bij stap {first_bingo_step} met {first_bingo_count} winnaar(s).")
                else:
                    st.info("Geen bingo gevallen binnen de geïmporteerde volgorde.")

                # Chronological list of bingo events
                if events:
                    st.write("Alle bingo’s in volgorde:")
                    # Sort by step, then by card
                    events.sort(key=lambda e: (e["step"], e["card"]))
                    for e in events:
                        details = []
                        if e["h"]:
                            details.append(f"Horizontaal x{e['h']}")
                        if e["v"]:
                            details.append(f"Verticaal x{e['v']}")
                        if e["d"]:
                            details.append(f"Diagonaal x{e['d']}")
                        detail_str = ", ".join(details) if details else ""
                        st.write(f"Stap {e['step']} — Kaart {e['card']}: {e['type']}" + (f" ({detail_str})" if detail_str else ""))
                else:
                    st.info("Geen bingo-events geregistreerd.")
    except Exception as e:
        st.error(f"Kon verhaal.html niet verwerken: {e}")

# -----------------------------
# Beautify verhaal.html (wrap images, add CSS, captions)
# -----------------------------
st.divider()
st.subheader("✨ Verhaal.html mooier maken (Beautify)")
beauty_file = st.file_uploader("Upload verhaal.html", type=["html", "htm"], key="beautify_verhaal_html")
if beauty_file is not None:
    try:
        raw = beauty_file.read().decode('utf-8', errors='ignore')
        import re
        # Extract all <a ...><img ...></a> blocks and wrap them in figure blocks with captions
        def wrap_figures(html: str) -> str:
            # Pattern to find anchor with img
            pattern = re.compile(r"<a[^>]*href=\"([^\"]+)\"[^>]*>\s*<img[^>]*src=\"([^\"]+)\"[^>]*alt=\"([^\"]*)\"[^>]*/?>\s*</a>", re.IGNORECASE)
            def repl(m):
                href, src, alt = m.group(1), m.group(2), m.group(3)
                caption = alt if alt else href
                return f"<div class=\"figure\"><a href=\"{href}\"><img src=\"{src}\" alt=\"{alt or src}\"></a><div class=\"caption\">{caption}</div></div>"
            return pattern.sub(repl, html)

        content = wrap_figures(raw)
        # Build pretty HTML shell
        pretty_head = """
<!DOCTYPE html>
<html lang=\"nl\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Verhaal</title>
  <style>
    :root { --bg:#fafafa; --fg:#1a1a1a; --muted:#666; --accent:#1e88e5; --card-bg:#fff; --card-border:#eee; --maxw:820px; }
    html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,system-ui,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
    .container{max-width:var(--maxw);margin:0 auto;padding:24px 16px 64px}
    header{margin:0 0 24px;padding:24px 0 8px;border-bottom:1px solid var(--card-border)}
    header h1{margin:0 0 6px;font-size:28px;font-weight:700;letter-spacing:-.02em}
    header p{margin:0;color:var(--muted);font-size:14px}
    main p{margin:16px 0;font-size:17px}
    .figure{margin:20px 0;display:flex;flex-direction:column;align-items:center}
    .figure a{display:inline-block;text-decoration:none;outline:none;border-radius:12px;background:var(--card-bg);border:1px solid var(--card-border);box-shadow:0 4px 16px rgba(0,0,0,.06);overflow:hidden;transition:transform .1s ease,box-shadow .2s ease}
    .figure a:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(0,0,0,.08)}
    .figure img{display:block;height:auto;width:min(100%,720px);max-width:100%}
    .caption{margin-top:8px;color:var(--muted);font-size:13px;text-align:center}
    a.inline{color:var(--accent);text-decoration:none;border-bottom:1px dashed rgba(30,136,229,.4)}
    a.inline:hover{border-bottom-color:var(--accent)}
    @media print{ :root{--bg:#fff} .figure a{box-shadow:none!important} }
  </style>
</head>
<body>
  <div class=\"container\">
    <header>
      <h1>Verhaal</h1>
      <p>Tekst en afbeeldingen in volgorde — klik op een afbeelding om de gekoppelde href te volgen.</p>
    </header>
    <main>
"""
        pretty_tail = """
    </main>
  </div>
</body>
</html>
"""
        # Try to extract body inner content; if not present, use full content
        body_match = re.search(r"<body[^>]*>([\s\S]*?)</body>", content, flags=re.IGNORECASE)
        inner = body_match.group(1) if body_match else content
        pretty_html = pretty_head + inner + pretty_tail

        st.download_button(
            label="Download verhaal_mooi.html",
            data=pretty_html.encode('utf-8'),
            file_name="verhaal_mooi.html",
            mime="text/html"
        )
        st.info("De HTML is opgeschoond en opgemaakt. Afbeeldingen zijn gewrapt in figure-blokken met captions. Tekst is behouden.")
    except Exception as e:
        st.error(f"Kon verhaal.html niet beautify-en: {e}")

