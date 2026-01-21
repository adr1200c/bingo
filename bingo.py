import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

# 2. Functie om een foto om te zetten naar Base64 (voorkomt laadproblemen op mobiel)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# 3. De "iPhone-proof" CSS
st.markdown("""
    <style>
    /* Forceer de hoofdcontainer om niet te breed te worden */
    .main .block-container {
        max-width: 250px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Forceer 3 kolommen strak naast elkaar */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
        width: 50% !important;
    }
    
    [data-testid="column"] {
        width: 33% !important;
        flex: 1 1 33% !important;
        min-width: 0px !important;
    }

    /* DE FIX: Dwing de foto in een vierkant binnen de kolombreedte */
    .bingo-photo {
        width: 100% !important;
        max-width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        object-fit: cover !important;
        border-radius: 8px;
        border: 2px solid #eeeeee;
        display: block;
    }

    /* Stijl voor gevonden foto's */
    .found {
        filter: grayscale(100%) opacity(0.3);
        border: 2px solid #4CAF50 !important;
    }

    /* Knoppen compact maken */
    .stButton>button {
        width: 100% !important;
        border-radius: 10px !important;
        height: 35px !important;
        padding: 0 !important;
        font-size: 14px !important;
        margin-top: 5px !important;
    }

    /* Titel centreren */
    h1 {
        text-align: center;
        font-size: 24px !important;
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
        st.warning("Voeg minimaal 9 foto's toe aan de map.")
    else:
        # Initialiseer bingokaart in sessie
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = random.sample(all_photos, 9)
            st.session_state.found = [False] * 9

        # 4. Het 3x3 Grid bouwen
        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                idx = row * 3 + col
                with cols[col]:
                    photo_name = st.session_state.my_cards[idx]
                    is_found = st.session_state.found[idx]
                    img_path = os.path.join(IMAGE_DIR, photo_name)
                    
                    try:
                        # Haal foto data op
                        img_base64 = get_base64_image(img_path)
                        extension = photo_name.split('.')[-1]
                        
                        # HTML weergave voor maximale controle op mobiel
                        status_class = "found" if is_found else ""
                        st.markdown(f"""
                            <img src="data:image/{extension};base64,{img_base64}" 
                                 class="bingo-photo {status_class}">
                            """, unsafe_allow_html=True)
                        
                        # Interactie knop
                        label = "✅" if is_found else "Kies"
                        if st.button(label, key=f"btn_{idx}"):
                            st.session_state.found[idx] = not st.session_state.found[idx]
                            st.rerun()
                    except Exception:
                        st.write("⚠️")

        # Bingo effect
        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

# 5. Reset en instructie
st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()

st.caption("Tip: Tik op 'Kies' als je de foto herkent in het verhaal.")