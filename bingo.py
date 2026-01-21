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
    st.error("Map 'familie_fotos' niet gevonden.")
else:
    all_photos = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])

    if len(all_photos) < 9:
        st.warning("Voeg minimaal 9 foto's toe aan de map.")
    else:
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = random.sample(all_photos, 9)

        b64_list = [get_base64_image(os.path.join(IMAGE_DIR, name)) for name in st.session_state.my_cards]

        # De meest stabiele HTML/JS versie zonder extra knoppen
        html_code = f"""
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
            <style>
                body {{ margin: 0; background: transparent; overflow: hidden; display: flex; justify-content: center; }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 8px;
                    width: 98vw;
                    max-width: 400px;
                    padding: 5px;
                }}
                .item {{
                    position: relative;
                    aspect-ratio: 1 / 1;
                    border-radius: 10px;
                    overflow: hidden;
                    border: 2px solid #ddd;
                    cursor: pointer;
                    -webkit-tap-highlight-color: transparent;
                }}
                img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    pointer-events: none;
                }}
                .cross {{
                    position: absolute;
                    top: 0; left: 0; width: 100%; height: 100%;
                    display: none;
                    pointer-events: none;
                    z-index: 10;
                }}
                .cross::before, .cross::after {{
                    content: '';
                    position: absolute;
                    top: 50%; left: 5%;
                    width: 90%;
                    height: 12px;
                    background: rgba(220, 20, 60, 0.85);
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

            <script>
                function toggle(el) {{
                    el.classList.toggle('selected');
                    const totalSelected = document.querySelectorAll('.selected').length;
                    if (totalSelected === 9) {{
                        confetti({{
                            particleCount: 150,
                            spread: 70,
                            origin: {{ y: 0.6 }}
                        }});
                    }}
                }}
            </script>
        </body>
        </html>
        """

        st.components.v1.html(html_code, height=450)

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()