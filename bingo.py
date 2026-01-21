import streamlit as st
import random
import os
import base64

st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 1. DE "IPHONE-KILLER" CSS
st.markdown("""
    <style>
    /* Dwing de container smal */
    .block-container {
        padding: 5px !important;
        max-width: 380px !important;
    }

    /* We maken een eigen container voor de items */
    .bingo-grid-container {
        text-align: center;
        width: 100%;
        display: block;
    }

    /* Elk item is exact 30% breed en staat naast elkaar */
    .bingo-item {
        display: inline-block !important;
        width: 30% !important;
        margin: 1%;
        vertical-align: top;
    }

    .bingo-photo {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        object-fit: cover !important;
        border-radius: 6px;
        border: 1px solid #ddd;
    }

    .found {
        filter: grayscale(100%) opacity(0.3);
        border: 2px solid #4CAF50 !important;
    }

    /* Verberg de Streamlit kolom-structuur volledig */
    [data-testid="column"] {
        display: none !important;
    }

    /* Maak de knoppen klein genoeg voor in het vakje */
    div.stButton > button {
        width: 100% !important;
        font-size: 10px !important;
        height: 26px !important;
        padding: 0px !important;
        margin-top: 2px !important;
    }

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

        # 2. HET GRID BOUWEN (Zonder st.columns)
        # We gebruiken één grote div en zetten daar alles in
        
        # We gebruiken een trucje: we renderen de foto's en knoppen in een grid
        # door ze handmatig in een loop te zetten zonder Streamlit kolommen.
        
        for i in range(9):
            # We openen een 'vakje'
            with st.container():
                # Dit is de 'hack': we gebruiken markdown voor de foto 
                # en een gewone button voor de actie, maar de CSS dwingt ze naast elkaar.
                
                photo_name = st.session_state.my_cards[i]
                is_found = st.session_state.found[i]
                img_path = os.path.join(IMAGE_DIR, photo_name)
                
                try:
                    img_b64 = get_base64_image(img_path)
                    ext = photo_name.split('.')[-1]
                    status_class = "found" if is_found else ""
                    
                    # We maken een div die Streamlit's stacking negeert
                    st.markdown(f'''
                        <div style="float: left; width: 31%; margin: 1%;">
                            <img src="data:image/{ext};base64,{img_b64}" class="bingo-photo {status_class}">
                    ''', unsafe_allow_html=True)
                    
                    # De knop
                    label = "✅" if is_found else "Kies"
                    if st.button(label, key=f"btn_{i}"):
                        st.session_state.found[i] = not st.session_state.found[i]
                        st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                except:
                    st.write("!")

        # Clear fix om de floats te stoppen
        st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)

        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()