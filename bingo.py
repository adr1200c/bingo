import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.title("📸 Familie Bingo")

IMAGE_DIR = "familie_fotos"

if not os.path.exists(IMAGE_DIR):
    st.error("Map niet gevonden.")
else:
    all_photos = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])

    if len(all_photos) < 9:
        st.warning("Te weinig foto's.")
    else:
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = random.sample(all_photos, 9)

        b64_list = [get_base64_image(os.path.join(IMAGE_DIR, name)) for name in st.session_state.my_cards]

        # De HTML/JS bundel
        html_code = f"""
        <html>
        <head>
            <style>
                body {{ margin: 0; font-family: sans-serif; display: flex; justify-content: center; background: transparent; overflow: hidden; }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 10px;
                    width: 95vw;
                    max-width: 400px;
                    padding: 10px;
                }}
                .item {{
                    position: relative;
                    aspect-ratio: 1 / 1;
                    border-radius: 12px;
                    overflow: hidden;
                    border: 3px solid #eee;
                    cursor: pointer;
                    -webkit-tap-highlight-color: transparent;
                }}
                img {{ width: 100%; height: 100%; object-fit: cover; pointer-events: none; }}
                
                .cross {{
                    position: absolute;
                    top: 0; left: 0; width: 100%; height: 100%;
                    display: none; pointer-events: none; z-index: 10;
                }}
                .cross::before, .cross::after {{
                    content: ''; position: absolute; top: 50%; left: 5%;
                    width: 90%; height: 14px; background: rgba(220, 20, 60, 0.9);
                    border-radius: 10px;
                }}
                .cross::before {{ transform: translateY(-50%) rotate(45deg); }}
                .cross::after {{ transform: translateY(-50%) rotate(-45deg); }}

                .selected .cross {{ display: block; }}
                .selected img {{ filter: grayscale(100%) opacity(0.4); }}
            </style>
        </head>
        <body>
            <div class="grid">
                {"".join([f'<div class="item" onclick="toggle(this)"><img src="data:image/jpeg;base64,{b64}"><div class="cross"></div></div>' for b64 in b64_list])}
            </div>

            <audio id="click-sound" src="https://www.soundjay.com/buttons/sounds/button-37.mp3" preload="auto"></audio>

            <script>
                const sound = document.getElementById('click-sound');
                
                function toggle(el) {{
                    el.classList.toggle('selected');
                    sound.currentTime = 0;
                    sound.play();

                    const totalSelected = document.querySelectorAll('.selected').length;
                    // We sturen alleen een bericht als de bingo echt gehaald is (9 stuks)
                    if (totalSelected === 9) {{
                        // Geef een kleine vertraging zodat het kruisje eerst getekend wordt
                        setTimeout(() => {{
                            window.parent.postMessage({{
                                type: 'streamlit:setComponentValue', 
                                value: 'BINGO_NOW' 
                            }}, '*');
                        }}, 300);
                    }}
                }}
            </script>
        </body>
        </html>
        """

        # Belangrijk: De 'result' vangt nu alleen de waarde 'BINGO_NOW' op
        result = st.components.v1.html(html_code, height=480)
        
        # Alleen ballonnen als de specifieke tekst 'BINGO_NOW' binnenkomt
        if result == "BINGO_NOW":
            st.balloons()
            st.success("🎉 GEWELDIG! Je hebt BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()