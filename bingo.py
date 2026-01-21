import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

# 2. Functie voor Base64 afbeeldingen
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# 3. CSS die GEEN gebruik maakt van Streamlit kolommen
st.markdown("""
    <style>
    /* Verwijder Streamlit marges */
    .block-container {
        padding: 10px !important;
        max-width: 100% !important;
    }

    /* HET GRID: Dit dwingt 3 kolommen af, ongeacht het apparaat */
    .bingo-grid {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
        margin: 0 auto !important;
    }

    .bingo-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }

    .bingo-photo {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        object-fit: cover !important;
        border-radius: 8px;
        border: 1px solid #ddd;
        cursor: pointer;
    }

    .found {
        filter: grayscale(100%) opacity(0.3);
        border: 3px solid #4CAF50 !important;
    }

    /* Verberg standaard Streamlit elementen die in de weg zitten */
    [data-testid="column"] { display: none !important; }
    [data-testid="stHorizontalBlock"] { display: block !important; }
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

        # 4. We bouwen het Grid VOLLEDIG in HTML
        # Omdat we actie willen (klikken), gebruiken we buttons die eruitzien als de foto's
        
        grid_html = '<div class="bingo-grid">'
        
        for i in range(9):
            photo_name = st.session_state.my_cards[i]
            is_found = st.session_state.found[i]
            img_path = os.path.join(IMAGE_DIR, photo_name)
            
            try:
                img_base64 = get_base64_image(img_path)
                ext = photo_name.split('.')[-1]
                status_class = "found" if is_found else ""
                
                # We maken een onzichtbare Streamlit knop per foto
                # Maar we tonen de foto in het grid
                with st.container():
                    st.markdown(f"""
                        <div class="bingo-item">
                            <img src="data:image/{ext};base64,{img_base64}" class="bingo-photo {status_class}">
                        </div>
                    """, unsafe_allow_html=True)
                    
                    label = "✅" if is_found else f"Foto {i+1}"
                    if st.button(label, key=f"btn_{i}"):
                        st.session_state.found[i] = not st.session_state.found[i]
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