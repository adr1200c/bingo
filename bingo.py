import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 2. De CSS voor het Grid en het Kruis
st.markdown("""
    <style>
    /* Dwing 3 kolommen naast elkaar op iPhone */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        gap: 6px !important;
    }
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }

    /* De Klikbare Container */
    .bingo-link {
        text-decoration: none !important;
        display: block;
        width: 100%;
        position: relative;
    }

    .photo-box {
        position: relative;
        width: 100%;
        aspect-ratio: 1 / 1;
        border-radius: 8px;
        overflow: hidden;
        border: 2px solid #ddd;
    }

    .bingo-photo {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    /* Het Viltstift Kruis */
    .cross {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        display: none;
        z-index: 2;
    }
    .cross::before, .cross::after {
        content: '';
        position: absolute;
        top: 50%; left: 5%;
        width: 90%; height: 12px;
        background: rgba(220, 20, 60, 0.8);
        border-radius: 10px;
    }
    .cross::before { transform: translateY(-50%) rotate(45deg); }
    .cross::after { transform: translateY(-50%) rotate(-45deg); }

    .is-found .cross { display: block; }
    .is-found .bingo-photo { filter: grayscale(100%) opacity(0.4); }

    h1 { text-align: center; font-size: 22px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 Familie Bingo")

IMAGE_DIR = "familie_fotos"

if not os.path.exists(IMAGE_DIR):
    st.error(f"Map '{IMAGE_DIR}' niet gevonden.")
else:
    all_photos = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])

    if len(all_photos) < 9:
        st.warning("Te weinig foto's gevonden.")
    else:
        # Session state initialiseren
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = random.sample(all_photos, 9)
            st.session_state.found = [False] * 9

        # 3. LOGICA: Luister naar klikken via URL parameters
        query_params = st.query_params
        if "clicked" in query_params:
            clicked_idx = int(query_params["clicked"])
            # Toggle de status
            st.session_state.found[clicked_idx] = not st.session_state.found[clicked_idx]
            # Reset de URL om herhaling te voorkomen
            st.query_params.clear()
            st.rerun()

        # 4. Het Grid bouwen
        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                idx = row * 3 + col
                with cols[col]:
                    photo_name = st.session_state.my_cards[idx]
                    found_status = st.session_state.found[idx]
                    img_path = os.path.join(IMAGE_DIR, photo_name)
                    
                    try:
                        img_b64 = get_base64_image(img_path)
                        ext = photo_name.split('.')[-1]
                        found_class = "is-found" if found_status else ""
                        
                        # We maken van de hele foto een HTML link
                        # Deze link herlaadt de pagina met "?clicked=X"
                        st.markdown(f'''
                            <a href="/?clicked={idx}" target="_self" class="bingo-link">
                                <div class="photo-box {found_class}">
                                    <img src="data:image/{ext};base64,{img_b64}" class="bingo-photo">
                                    <div class="cross"></div>
                                </div>
                            </a>
                        ''', unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.write("!")

        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()