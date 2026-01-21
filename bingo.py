import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Rietman Familie Bingo", layout="centered")

# 2. Verberg Streamlit rommel (GitHub, Header, Footer)
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

IMAGE_DIR = "familie_fotos"

if not os.path.exists(IMAGE_DIR):
    st.error("Map 'familie_fotos' niet gevonden.")
else:
    all_photos = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])

    if len(all_photos) < 9:
        st.warning(f"Voeg minimaal 9 foto's toe.")
    else:
        # De sessie onthoudt de kaart zolang de gebruiker de pagina open heeft
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
                body {{ margin: 0; background: transparent; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }}
                #overlay {{
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: #ffffff; z-index: 100; display: flex; flex-direction: column;
                    justify-content: center; align-items: center; text-align: center;
                }}
                .btn-container {{ display: flex; flex-direction: column; gap: 15px; width: 280px; }}
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
            <div id="overlay">
                <h3 style="color: #333; margin-bottom: 25px;">Welkom bij de Rietman Bingo!</h3>
                <div class="btn-container">
                    <button class="start-btn" onclick="startBingo(true)">Speel met Geluid 🔊</button>
                    <button class="start-btn silent" onclick="startBingo(false)">Stil Spelen 🔇</button>
                </div>
            </div>

            <div id="game-container">
                <div class="grid" id="bingoGrid">
                    {"".join([f'<div class="item" onclick="toggle(this, event)"><img src="data:image/jpeg;base64,{b}"><div class="cross"></div></div>' for b in b64_list])}
                </div>
                <div class="instruction">
                    <b>Spelregels:</b> Tik op de foto die wordt getoond!<br>
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