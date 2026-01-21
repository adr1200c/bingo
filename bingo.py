import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# 2. De "Anti-Stacking" CSS
st.markdown("""
    <style>
    /* Zorg dat de titel niet wordt afgekapt en gecentreerd is */
    .main h1 {
        font-size: 22px !important;
        text-align: center !important;
        white-space: normal !important;
        line-height: 1.2 !important;
    }

    /* Dwing de container op de iPhone naar de volledige breedte */
    .block-container {
        padding: 10px !important;
        max-width: 100% !important;
    }

    /* Het Grid: we gebruiken Flexbox met 'nowrap' verbod */
    .bingo-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        width: 100%;
        gap: 6px;
    }

    /* Elk vakje is EXACT 30% van de breedte, zodat er altijd 3 passen */
    .bingo-box {
        width: 30% !important;
        margin-bottom: 10px;
        display: inline-block;
    }

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

    /* Knoppen fix voor iPhone */
    div.stButton > button {
        width: 100% !important;
        font-size: 12px !important;
        height: 32px !important;
        padding: 0px !important;
        margin-top: 4px !important;
    }

    /* Verberg de Streamlit kolommen die we als anker gebruiken */
    [data-testid="column"] {
        flex: 1 1 30% !important;
        min-width: 30% !important;
    }
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

        # 3. Het Grid bouwen
        # We gebruiken st.columns(3), maar de CSS hierboven dwingt ze om klein te blijven
        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                idx = row * 3 + col
                with cols[col]:
                    photo_name = st.session_state.my_cards[idx]
                    is_found = st.session_state.found[idx]
                    img_path = os.path.join(IMAGE_DIR, photo_name)
                    
                    try:
                        img_base64 = get_base64_image(img_path)
                        ext = photo_name.split('.')[-1]
                        status_class = "found" if is_found else ""
                        
                        # We tonen de foto
                        st.markdown(f"""
                            <img src="data:image/{ext};base64,{img_base64}" 
                                 class="bingo-photo {status_class}">
                        """, unsafe_allow_html=True)
                        
                        # De knop direct eronder
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