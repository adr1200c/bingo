import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

# 2. Functie om een foto om te zetten naar een tekst-link (Base64)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# 3. CSS voor het 3x3 grid en de foto-styling
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
    }
    [data-testid="column"] {
        width: 33% !important;
        flex: 1 1 33% !important;
        min-width: 0px !important;
    }
    /* De 'Magie': CSS dwingt de foto in een vierkant */
    .bingo-photo {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 10px;
        border: 2px solid #eeeeee;
        display: block;
    }
    .found {
        filter: grayscale(100%) opacity(0.3);
    }
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 Familie Bingo")

IMAGE_DIR = "familie_fotos"

if not os.path.exists(IMAGE_DIR):
    st.error(f"Map '{IMAGE_DIR}' niet gevonden.")
else:
    all_photos = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    if len(all_photos) < 9:
        st.warning("Voeg meer foto's toe.")
    else:
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = random.sample(all_photos, 9)
            st.session_state.found = [False] * 9

        # 4. Het 3x3 Grid
        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                idx = row * 3 + col
                with cols[col]:
                    photo_name = st.session_state.my_cards[idx]
                    is_found = st.session_state.found[idx]
                    img_path = os.path.join(IMAGE_DIR, photo_name)
                    
                    try:
                        # Zet foto om naar base64 data
                        img_base64 = get_base64_image(img_path)
                        img_type = photo_name.split('.')[-1]
                        
                        # Toon foto via HTML (omzeilt Streamlit image beperkingen op mobiel)
                        found_class = "found" if is_found else ""
                        st.markdown(f"""
                            <img src="data:image/{img_type};base64,{img_base64}" 
                                 class="bingo-photo {found_class}">
                            """, unsafe_allow_html=True)
                        
                        label = "✅" if is_found else "Kies"
                        if st.button(label, key=f"btn_{idx}"):
                            st.session_state.found[idx] = not st.session_state.found[idx]
                            st.rerun()
                    except Exception:
                        st.write("Fout")

        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()