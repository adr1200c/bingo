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

# Initialiseer de status voor de ballonnen
if "show_balloons" not in st.session_state:
    st.session_state.show_balloons = False

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

        # De HTML/JS met geluid en postMessage voor Streamlit ballonnen
        html_code = f"""
        <html>
        <head>
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
                {"".join([f'<div class="item" onclick="toggle(this, {i})"><img src="data:image/jpeg;base64,{b64}"><div class="cross"></div></div>' for i, b64 in enumerate(b64_list)])}
            </div>

            <audio id="click-sound" src="https://www.soundjay.com/buttons/sounds/button-37.mp3" preload="auto"></audio>

            <script>
                const sound = document.getElementById('click-sound');
                let audioUnlocked = false;
                let selectedItems = Array(9).fill(false); // Houd de status lokaal bij

                function toggle(el, index) {{
                    // De "Safari Unlock" truc voor audio
                    if (!audioUnlocked) {{
                        sound.play().then(() => {{
                            sound.pause();
                            sound.currentTime = 0;
                            audioUnlocked = true;
                        }}).catch(e => console.log("Audio awaiting user interaction..."));
                    }}

                    el.classList.toggle('selected');
                    selectedItems[index] = el.classList.contains('selected');
                    
                    if (audioUnlocked) {{
                        sound.currentTime = 0;
                        sound.play();
                    }}

                    const totalSelected = selectedItems.filter(Boolean).length;
                    if (totalSelected === 9) {{
                        // Stuur signaal naar Streamlit voor ballonnen
                        window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: 'BINGO_WIN' }}, '*');
                    }} else {{
                        // Zorg dat Streamlit geen valse Bingo-melding krijgt als niet alles vol is
                        window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: 'NOT_BINGO' }}, '*');
                    }}
                }}
            </script>
        </body>
        </html>
        """
        # Render het Iframe en vang het signaal voor de ballonnen op
        # De hoogte is aangepast voor een strakker grid
        streamlit_message = st.components.v1.html(html_code, height=450)
        
        # Alleen ballonnen als de specifieke boodschap 'BINGO_WIN' binnenkomt
        if streamlit_message == "BINGO_WIN":
            st.balloons()
            st.success("🎉 BINGO! De hele kaart is vol!")
            # Reset de status zodat de ballonnen niet blijven komen bij reruns
            st.session_state.show_balloons = False 
        elif streamlit_message == "NOT_BINGO":
            # Dit voorkomt dat ballonnen verschijnen als de pagina opnieuw laadt 
            # en de status van de selectie nog niet volledig is
            st.session_state.show_balloons = False

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun() # Herlaad de hele app om een nieuwe kaart te genereren