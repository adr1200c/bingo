import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

# 2. Verberg Streamlit rommel
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .block-container { padding-top: 2rem; }
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

st.title("📸 Familie Bingo")

IMAGE_DIR = "familie_fotos"

if not os.path.exists(IMAGE_DIR):
    st.error("Map 'familie_fotos' niet gevonden.")
else:
    all_photos = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])

    if len(all_photos) < 9:
        st.warning("Voeg minimaal 9 foto's toe.")
    else:
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = random.sample(all_photos, 9)

        paths = [os.path.join(IMAGE_DIR, name) for name in st.session_state.my_cards]
        b64_list = []
        for p in paths:
            b64 = get_base64_image(p)
            if b64:
                b64_list.append(b64)
        
        html_code = f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
            <style>
                body {{ margin: 0; background: transparent; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }}
                #overlay {{
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: #f8f9fa; z-index: 100; display: flex; flex-direction: column;
                    justify-content: center; align-items: center; text-align: center;
                }}
                .btn-container {{ display: flex; flex-direction: column; gap: 15px; width: 280px; }}
                .start-btn {{ padding: 20px; font-size: 18px; cursor: pointer; background: linear-gradient(135deg, #42a5f5, #1e88e5); color: white; border: none; border-radius: 15px; font-weight: bold; }}
                .start-btn.silent {{ background: #757575; }}
                #game-container {{ display: none; flex-direction: column; align-items: center; width: 95vw; max-width: 400px; }}
                .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; width: 100%; margin-bottom: 20px; }}
                .item {{ position: relative; aspect-ratio: 1/1; border-radius: 10px; overflow: hidden; border: 3px solid #fff; cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                img {{ width: 100%; height: 100%; object-fit: cover; }}
                .cross {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: none; pointer-events: none; z-index: 10; }}
                .cross::before, .cross::after {{ content: ''; position: absolute; top: 50%; left: 10%; width: 80%; height: 12px; background: rgba(230, 0, 0, 0.8); border-radius: 5px; }}
                .cross::before {{ transform: translateY(-50%) rotate(45deg); }}
                .cross::after {{ transform: translateY(-50%) rotate(-45deg); }}
                .selected .cross {{ display: block; }}
                .selected img {{ filter: grayscale(100%) brightness(0.5); }}
                .instruction {{ color: #444; font-style: italic; font-size: 16px; text-align: center; background: #eee; padding: 10px; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <div id="overlay">
                <h3 style="color: #333;">Kies je modus:</h3>
                <div class="btn-container">
                    <button class="start-btn" onclick="startBingo(true)">Speel met Geluid 🔊</button>
                    <button class="start-btn silent" onclick="startBingo(false)">Stil Spelen 🔇</button>
                </div>
            </div>

            <div id="game-container">
                <div class="grid" id="bingoGrid">
                    {"".join([f'<div class="item" data-index="{i}" onclick="toggle(this, event)"><img src="data:image/jpeg;base64,{b}"><div class="cross"></div></div>' for i, b in enumerate(b64_list)])}
                </div>
                <div class="instruction">💡 Klik op de foto uit het Rietman verhaal!<br><b>3 op een rij = Bingo! | 9 foto's = Hoofdprijs!</b></div>
            </div>

            <audio id="clickSound" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"></audio>
            <audio id="winSound" src="https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3"></audio>

            <script>
                const clickSnd = document.getElementById('clickSound');
                const winSnd = document.getElementById('winSound');
                let soundEnabled = true;
                let win3Reached = false;
                let win9Reached = false;

                function startBingo(s) {{
                    soundEnabled = s;
                    if(s) {{ clickSnd.play().then(()=>{{clickSnd.pause();}}).catch(()=>{{" "}}); }}
                    document.getElementById('overlay').style.display = 'none';
                    document.getElementById('game-container').style.display = 'flex';
                }}

                function check3InARow() {{
                    const items = document.querySelectorAll('.item');
                    const selected = Array.from(items).map(el => el.classList.contains('selected'));
                    const winPatterns = [
                        [0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]
                    ];
                    return winPatterns.some(pattern => pattern.every(index => selected[index]));
                }}

                function toggle(el, ev) {{
                    const isSel = !el.classList.contains('selected');
                    el.classList.toggle('selected');
                    
                    if(isSel) {{
                        if(soundEnabled) {{ clickSnd.currentTime=0; clickSnd.play(); }}
                        confetti({{ particleCount: 20, origin: {{ x: ev.clientX/window.innerWidth, y: ev.clientY/window.innerHeight }} }});
                    }}

                    const selectedCount = document.querySelectorAll('.selected').length;

                    // Check voor 3 op een rij (Eerste prijs)
                    if(!win3Reached && check3InARow()) {{
                        win3Reached = true;
                        if(soundEnabled) winSnd.play();
                        confetti({{ particleCount: 100, spread: 70, origin: {{ y: 0.6 }}, colors: ['#42a5f5', '#ffffff'] }});
                        setTimeout(() => alert("BINGO! Je hebt 3 op een rij! Speel door voor de hoofdprijs (9 foto's)!"), 500);
                    }}

                    // Check voor alle 9 (Hoofdprijs)
                    if(!win9Reached && selectedCount === 9) {{
                        win9Reached = true;
                        if(soundEnabled) winSnd.play();
                        
                        // Extra grote confetti regen
                        var end = Date.now() + (5 * 1000);
                        (function frame() {{
                            confetti({{ particleCount: 7, angle: 60, spread: 55, origin: {{ x: 0 }}, colors: ['#ff0000', '#ffd700'] }});
                            confetti({{ particleCount: 7, angle: 120, spread: 55, origin: {{ x: 1 }}, colors: ['#ff0000', '#ffd700'] }});
                            if (Date.now() < end) {{ requestAnimationFrame(frame); }}
                        }}());
                        
                        setTimeout(() => alert("HOOFDPRIJS!!! Je hebt de hele kaart vol! 🏆"), 1000);
                    }}
                }}
            </script>
        </body>
        </html>
        """
        st.components.v1.html(html_code, height=650)

st.divider()
if st.button("🔄 Nieuwe kaart genereren"):
    st.session_state.pop("my_cards", None)
    st.rerun()