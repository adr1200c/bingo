import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 2. De "Onbreekbare" CSS
st.markdown("""
    <style>
    /* Maak de pagina geschikt voor mobiel */
    .block-container {
        padding: 5px !important;
        max-width: 100% !important;
    }

    /* DE TABEL: Safari MOET dit naast elkaar zetten */
    .bingo-table {
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        margin-top: 10px;
    }

    .bingo-cell {
        width: 33.33%;
        padding: 4px;
        text-align: center;
    }

    .img-container {
        position: relative;
        width: 100%;
        aspect-ratio: 1 / 1;
    }

    .bingo-photo {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 8px;
        border: 2px solid #eee;
        display: block;
    }

    .found {
        filter: grayscale(100%) opacity(0.3);
        border: 2px solid #4CAF50;
    }

    /* Verberg de lelijke standaard kolommen van Streamlit */
    [data-testid="column"] {
        display: none !important;
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

        # 3. Bouw de tabel handmatig
        # We gebruiken een combinatie van HTML voor de look en st.button voor de klik
        
        # We maken 3 rijen
        for r in range(3):
            # We gebruiken st.columns ALLEEN om de buttons op hun plek te krijgen
            # Maar we dwingen de breedte in de browser
            st.markdown('<style>[data-testid="column"] { display: block !important; width: 31% !important; float: left !important; }</style>', unsafe_allow_html=True)
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
                        
                        # Toon de foto in een HTML div
                        st.markdown(f"""
                            <div class="img-container">
                                <img src="data:image/{ext};base64,{img_b64}" class="bingo-photo {status_class}">
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # De klik-knop
                        label = "✅" if is_found else "Kies"
                        if st.button(label, key=f"btn_{idx}"):
                            st.session_state.found[idx] = not st.session_state.found[idx]
                            st.rerun()
                    except:
                        st.write("!")
            
            # Voeg een "clear fix" toe om te voorkomen dat rijen in elkaar schuiven
            st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)

        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()