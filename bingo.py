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
            st.session_state.found = [False] * 9

        # 2. HET GRID BOUWEN
        # We gebruiken GEEN st.columns meer. We gebruiken een simpele 3x3 loop.
        
        # CSS voor de iPhone fix
        st.markdown("""
            <style>
            /* Dit verwijdert de marges die Streamlit toevoegt */
            .block-container { padding: 5px !important; }
            
            /* Dwing de kolommen horizontaal ongeacht het apparaat */
            div[data-testid="column"] {
                width: 32% !important;
                flex: 0 0 32% !important;
                min-width: 32% !important;
                display: block !important;
                float: left !important;
            }
            
            /* Dwing de foto in een vierkant */
            .bingo-photo {
                width: 100% !important;
                aspect-ratio: 1 / 1 !important;
                object-fit: cover !important;
                border-radius: 8px;
                border: 2px solid #eee;
            }
            
            .found {
                filter: grayscale(100%) opacity(0.3);
                border: 2px solid #4CAF50 !important;
            }

            /* Knop styling */
            div.stButton > button {
                width: 100% !important;
                font-size: 10px !important;
                height: 28px !important;
                padding: 0px !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # 3. De kaarten tonen
        for r in range(3):
            cols = st.columns(3)
            for c in range(3):
                idx = r * 3 + c
                with cols[c]:
                    photo_name = st.session_state.my_cards[idx]
                    is_found = st.session_state.found[idx]
                    img_path = os.path.join(IMAGE_DIR, photo_name)
                    
                    try:
                        img_b64 = get_base64_image(img_path)
                        ext = photo_name.split('.')[-1]
                        status_class = "found" if is_found else ""
                        
                        # Directe HTML injectie voor de foto
                        st.markdown(f'''<img src="data:image/{ext};base64,{img_b64}" class="bingo-photo {status_class}">''', unsafe_allow_html=True)
                        
                        # De knop
                        label = "✅" if is_found else "Kies"
                        if st.button(label, key=f"btn_{idx}"):
                            st.session_state.found[idx] = not st.session_state.found[idx]
                            st.rerun()
                    except:
                        st.write("!")
            
            # Voorkom dat rijen in elkaar schuiven
            st.write('<div style="clear: both;"></div>', unsafe_allow_html=True)

        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()