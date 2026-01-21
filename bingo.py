import streamlit as st
import random
import os
import base64

st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 1. CSS voor compacte foto's ZONDER loze ruimte
st.markdown("""
    <style>
    /* Dwing de kolommen om strak in het midden naast elkaar te staan */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important; /* Zet de 3 foto's in het midden */
        gap: 8px !important; /* De enige ruimte tussen de foto's */
    }

    [data-testid="column"] {
        width: 100px !important;
        min-width: 100px !important;
        flex: 0 0 100px !important; /* Voorkomt dat de kolom groter wordt dan de foto */
        padding: 0px !important;
        margin: 0px !important;
    }

    .bingo-photo {
        width: 100px !important;
        height: 100px !important;
        object-fit: cover !important;
        border-radius: 8px;
        border: 2px solid #eee;
        display: block;
    }

    .found {
        filter: grayscale(100%) opacity(0.3);
        border: 2px solid #4CAF50 !important;
    }

    div.stButton > button {
        width: 100px !important;
        font-size: 11px !important;
        height: 28px !important;
        padding: 0px !important;
        margin-top: 4px !important;
    }

    h1 { text-align: center; font-size: 20px !important; }
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

        # 2. Het Grid bouwen
        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                idx = row * 3 + col
                with cols[col]:
                    photo_name = st.session_state.my_cards[idx]
                    is_found = st.session_state.found[idx]
                    img_path = os.path.join(IMAGE_DIR, photo_name)
                    
                    try:
                        img_b64 = get_base64_image(img_path)
                        ext = photo_name.split('.')[-1]
                        status_class = "found" if is_found else ""
                        
                        st.markdown(f'''<img src="data:image/{ext};base64,{img_b64}" class="bingo-photo {status_class}">''', unsafe_allow_html=True)
                        
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