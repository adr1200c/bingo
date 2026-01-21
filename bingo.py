import streamlit as st
import random
import os
import base64

# Configuratie
st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

st.title("📸 Familie Bingo")

IMAGE_DIR = "familie_fotos"

if not os.path.exists(IMAGE_DIR):
    st.error("Map 'familie_fotos' niet gevonden. Maak een map genaamd 'familie_fotos' aan en zet daar je afbeeldingen in.")
else:
    all_photos = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])

    if len(all_photos) < 9:
        st.warning("Voeg minimaal 9 foto's toe aan de map.")
    else:
        # Kies willekeurig 9 foto's
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = random.sample(all_photos, 9)

        # Zet afbeeldingen om naar Base64
        paths = [os.path.join(IMAGE_DIR, name) for name in st.session_state.my_cards]
        b64_list = []
        for p in paths:
            b64 = get_base64_image(p)
            if b64:
                b64_list.append(b64)
        
        if len(b64_list) != 9:
            st.error("Sommige afbeeldingen konden niet geladen worden.")
            st.stop()

        # De HTML, CSS en JavaScript code
        html_code = f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
            <style>
                body {{ 
                    margin: 0; 
                    background: transparent; 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    height: 100vh; 
                    overflow: hidden; 
                }}
                
                #overlay {{
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: #f8f9fa; z-index: 100; display: flex; flex-direction: column;
                    justify-content: center; align-items: center; text-align: center;
                }}

                .btn-container {{
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                    width: 80%;
                    max-width: 300px;
                }}
                
                .start-btn {{
                    padding: 20px; font-size: 20px; cursor: pointer;
                    background: linear-gradient(135deg, #42a5f5, #1e88e5); color: white; border: none;
                    border-radius: 15px; box-shadow: 0 6px 15px rgba(30, 136, 229, 0.3);
                    font-weight: bold; transition: 0.2s;
                }}

                .start-btn.silent {{
                    background: linear-gradient(135deg, #757575, #424242);
                    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
                }}

                .start-btn:active {{ transform: scale(0.95); }}

                .grid {{
                    display: grid; grid-template-columns: repeat(3, 1fr);
                    gap: 12px; width: 95vw; max-width: 420px; padding: 10px;
                    display: none;
                }}

                .item {{
                    position: relative; aspect-ratio: 1 / 1; border-radius: 12px;
                    overflow: hidden; border: 3px solid #fff; cursor: pointer;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    -webkit-tap-highlight-color: transparent; transition: transform 0.1s;
                }}

                .item:active {{ transform: scale(0.92); }}
                img {{ width: 100%; height: 100%; object-fit: cover; pointer-events: none; }}
                
                .cross {{
                    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                    display: none; pointer-events: none; z-index: 10;
                }}

                .cross::before, .cross::after {{
                    content: ''; position: absolute; top: 50%; left: 10%;
                    width: 80%; height: 12px; background: rgba(230, 0, 0, 0.85);
                    border-radius: 10px;
                }}
                .cross::before {{ transform: translateY(-50%) rotate(45deg); }}
                .cross::after {{ transform: translateY(-50%) rotate(-45deg); }}
                
                .selected .cross {{ display: block; }}
                .selected img {{ filter: grayscale(100%) brightness(0.6); }}
            </style>
        </head>
        <body>
            <div id="overlay">
                <h2 style="margin-bottom: 25px; color: #333;">Kies je speelstijl</h2>
                <div class="btn-container">
                    <button class="start-btn" onclick="startBingo(true)">Met Geluid 🔊</button>
                    <button class="start-btn silent" onclick="startBingo(false)">Zonder Geluid 🔇</button>
                </div>
            </div>

            <div class="grid" id="bingoGrid">
                {"".join([f'<div class="item" onclick="toggle(this, event)"><img src="data:image/jpeg;base64,{b}"><div class="cross"></div></div>' for b in b64_list])}
            </div>

            <audio id="clickSound" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" preload="auto"></audio>
            <audio id="winSound" src="https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3" preload="auto"></audio>

            <script>
                const clickSnd = document.getElementById('clickSound');
                const winSnd = document.getElementById('winSound');
                const overlay = document.getElementById('overlay');
                const grid = document.getElementById('bingoGrid');
                let soundEnabled = true;

                function startBingo(enableSound) {{
                    soundEnabled = enableSound;
                    
                    if (soundEnabled) {{
                        // Audio unlock voor mobiele browsers
                        clickSnd.play().then(() => {{ clickSnd.pause(); clickSnd.currentTime = 0; }}).catch(e => {{}});
                        winSnd.play().then(() => {{ winSnd.pause(); winSnd.currentTime = 0; }}).catch(e => {{}});
                    }}
                    
                    overlay.style.display = 'none';
                    grid.style.display = 'grid';
                }}

                function toggle(el, event) {{
                    const isSelecting = !el.classList.contains('selected');
                    el.classList.toggle('selected');
                    
                    if (isSelecting) {{
                        if (soundEnabled) {{
                            clickSnd.currentTime = 0;
                            clickSnd.play().catch(e => {{}});
                        }}
                        
                        confetti({{
                            particleCount: 25, spread: 50,
                            origin: {{ x: event.clientX / window.innerWidth, y: event.clientY / window.innerHeight }},
                            colors: ['#42a5f5', '#ffffff', '#ffeb3b']
                        }});
                    }}

                    const totalSelected = document.querySelectorAll('.selected').length;
                    if (totalSelected === 9) {{
                        if (soundEnabled) {{
                            winSnd.play().catch(e => {{}});
                        }}

                        var duration = 5 * 1000;
                        var end = Date.now() + duration;
                        (function frame() {{
                          confetti({{ particleCount: 5, angle: 60, spread: 55, origin: {{ x: 0 }}, colors: ['#FFD700', '#FFA500'] }});
                          confetti({{ particleCount: 5, angle: 120, spread: 55, origin: {{ x: 1 }}, colors: ['#FFD700', '#FFA500'] }});
                          if (Date.now() < end) {{ requestAnimationFrame(frame); }}
                        }}());
                    }}
                }}
            </script>
        </body>
        </html>
        """
        # Streamlit component om de HTML weer te geven
        st.components.v1.html(html_code, height=600)

# Knop om een nieuwe kaart te genereren
st.divider()
if st.button("🔄 Nieuwe kaart genereren"):
    st.session_state.pop("my_cards", None)
    st.rerun()