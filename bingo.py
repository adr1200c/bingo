import streamlit as st
import random
import os
import base64

st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

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

        b64_list = [get_base64_image(os.path.join(IMAGE_DIR, name)) for name in st.session_state.my_cards]

        html_code = f"""
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
            <style>
                body {{ margin: 0; background: transparent; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }}
                
                /* Startscherm Overlay */
                #overlay {{
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: white; z-index: 100; display: flex; flex-direction: column;
                    justify-content: center; align-items: center;
                }}
                .start-btn {{
                    padding: 20px 40px; font-size: 24px; cursor: pointer;
                    background-color: #28a745; color: white; border: none;
                    border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    transition: transform 0.2s;
                }}
                .start-btn:active {{ transform: scale(0.95); }}

                /* Bingo Grid */
                .grid {{
                    display: grid; grid-template-columns: repeat(3, 1fr);
                    gap: 8px; width: 98vw; max-width: 400px; padding: 5px;
                    display: none; /* Verberg grid tot start */
                }}
                .item {{
                    position: relative; aspect-ratio: 1 / 1; border-radius: 12px;
                    overflow: hidden; border: 2px solid #ddd; cursor: pointer;
                    -webkit-tap-highlight-color: transparent;
                }}
                img {{ width: 100%; height: 100%; object-fit: cover; pointer-events: none; }}
                .cross {{
                    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                    display: none; pointer-events: none; z-index: 10;
                }}
                .cross::before, .cross::after {{
                    content: ''; position: absolute; top: 50%; left: 5%;
                    width: 90%; height: 12px; background: rgba(220, 20, 60, 0.9);
                    border-radius: 10px;
                }}
                .cross::before {{ transform: translateY(-50%) rotate(45deg); }}
                .cross::after {{ transform: translateY(-50%) rotate(-45deg); }}
                .selected .cross {{ display: block; }}
                .selected img {{ filter: grayscale(100%) opacity(0.4); }}
            </style>
        </head>
        <body>
            <div id="overlay">
                <button class="start-btn" onclick="activateAudio()">▶ Start Bingo (met geluid)</button>
                <p style="margin-top: 15px; color: #666;">Tik om de kaart te laden</p>
            </div>

            <div class="grid" id="bingoGrid">
                {"".join([f'<div class="item" onclick="toggle(this, event)"><img src="data:image/jpeg;base64,{b}"><div class="cross"></div></div>' for b in b64_list])}
            </div>

            <audio id="click-sound" src="https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3" preload="auto"></audio>

            <script>
                const sound = document.getElementById('click-sound');
                const overlay = document.getElementById('overlay');
                const grid = document.getElementById('bingoGrid');

                function activateAudio() {{
                    // Safari Unlock: Speel af en pauzeer direct
                    sound.play().then(() => {{
                        sound.pause();
                        sound.currentTime = 0;
                        // Verberg overlay en toon grid
                        overlay.style.display = 'none';
                        grid.style.display = 'grid';
                    }}).catch(e => {{
                        console.error("Audio error:", e);
                        overlay.style.display = 'none';
                        grid.style.display = 'grid';
                    }});
                }}

                function toggle(el, event) {{
                    const isSelecting = !el.classList.contains('selected');
                    el.classList.toggle('selected');
                    
                    // Speel geluid
                    sound.currentTime = 0;
                    sound.play();

                    // Confetti bij elke klik
                    if (isSelecting) {{
                        confetti({{
                            particleCount: 30, spread: 50,
                            origin: {{ x: event.clientX / window.innerWidth, y: event.clientY / window.innerHeight }}
                        }});
                    }}

                    // Check Bingo
                    const totalSelected = document.querySelectorAll('.selected').length;
                    if (totalSelected === 9) {{
                        var duration = 4 * 1000;
                        var end = Date.now() + duration;
                        (function frame() {{
                          confetti({{ particleCount: 7, angle: 60, spread: 55, origin: {{ x: 0 }} }});
                          confetti({{ particleCount: 7, angle: 120, spread: 55, origin: {{ x: 1 }} }});
                          if (Date.now() < end) {{ requestAnimationFrame(frame); }}
                        }}());
                    }}
                }}
            </script>
        </body>
        </html>
        """
        st.components.v1.html(html_code, height=500)

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()