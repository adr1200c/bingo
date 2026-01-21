import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

# 2. CSS die de tabel en foto's dwingt
st.markdown("""
    <style>
    /* Dwing de hele app-container smal te blijven */
    .block-container {
        max-width: 100% !important;
        padding: 5px !important;
    }

    /* DE TABEL FIX */
    .bingo-table {
        width: 100% !important;
        table-layout: fixed !important; /* Dwingt gelijke kolommen */
        border-collapse: collapse !important;
    }

    .bingo-cell {
        width: 33.3% !important;
        padding: 4px !important;
        text-align: center;
        vertical-align: top;
    }

    .bingo-photo {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        object-fit: cover !important;
        border-radius: 8px;
        border: 2px solid #eee;
        display: block;
    }

    .found {
        filter: grayscale(100%) opacity(0.3);
        border: 2px solid #4CAF50 !important;
    }

    /* Maak Streamlit knoppen passend voor de tabel */
    div.stButton > button {
        width: 100% !important;
        font-size: 11px !important;
        height: 28px !important;
        padding: 0px !important;
        margin-top: 4px !important;
    }

    /* Titel fix */
    h1 { font-size: 20px !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

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

        # 3. De HTML Tabel genereren
        # We gebruiken st.columns alleen als 'anker' voor de buttons, 
        # maar de layout wordt bepaald door onze CSS en de HTML structuur.
        
        for r in range(3):
            cols = st.columns(3) # Streamlit maakt de kolommen
            for c in range(3):
                idx = r * 3 + c
                with cols[c]:
                    # We injecteren de foto via HTML in de kolom
                    photo_name = st.session_state.my_cards[idx]
                    is_found = st.session_state.found[idx]
                    img_path = os.path.join(IMAGE_DIR, photo_name)
                    
                    try:
                        img_b64 = get_base64_image(img_path)
                        ext = photo_name.split('.')[-1]
                        status_class = "found" if is_found else ""
                        
                        # De foto tonen
                        st.markdown(f"""
                            <img src="data:image/{ext};base64,{img_b64}" class="bingo-photo {status_class}">
                        """, unsafe_allow_html=True)
                        
                        # De button van Streamlit direct eronder
                        # Omdat de kolom via CSS gedwongen wordt op 33%, MOET de foto krimpen.
                        label = "✅" if is_found else "Kies"
                        if st.button(label, key=f"btn_{idx}"):
                            st.session_state.found[idx] = not st.session_state.found[idx]
                            st.rerun()
                    except:
                        st.write("!")

        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()