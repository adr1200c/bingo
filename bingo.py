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

# 3. DE FORCEER-CODE: CSS die kolommen verbiedt om onder elkaar te springen
st.markdown("""
    <style>
    /* Verwijder alle standaard padding van Streamlit */
    .block-container {
        padding: 10px !important;
        max-width: 400px !important;
    }

    /* HET ECHTE GRID: Dit kan niet breken op mobiel */
    .bingo-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        width: 100%;
        margin-top: 20px;
    }

    .bingo-card {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .bingo-photo {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 8px;
        border: 2px solid #ddd;
    }

    .found {
        filter: grayscale(100%) opacity(0.4);
        border: 2px solid #4CAF50 !important;
    }

    /* Zorg dat de knoppen van Streamlit in het grid passen */
    div.stButton > button {
        width: 100% !important;
        height: 30px !important;
        padding: 0px !important;
        font-size: 12px !important;
        margin-top: 5px !important;
    }
    
    /* Verberg de standaard Streamlit kolom-divs die we niet gebruiken */
    [data-testid="column"] {
        width: 0px !important;
        flex: 0 0 0% !important;
        min-width: 0px !important;
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 Familie Bingo")

IMAGE_DIR = "familie_fotos"

if not os.path.exists(IMAGE_DIR):
    st.error("Map niet gevonden.")
else:
    all_photos = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    if len(all_photos) < 9:
        st.warning("Te weinig foto's.")
    else:
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = random.sample(all_photos, 9)
            st.session_state.found = [False] * 9

        # 4. Het handmatige Grid bouwen
        # We gebruiken één grote container en steken daar alles in
        grid_html = '<div class="bingo-container">'
        
        # Omdat Streamlit knoppen niet in pure HTML kunnen, 
        # gebruiken we een mix, maar dwingen we de layout.
        
        # We maken 3 rijen handmatig
        for row in range(3):
            cols = st.columns(3) # We gebruiken ze, maar de CSS hierboven fixt de breedte
            for col in range(3):
                idx = row * 3 + col
                with cols[col]:
                    # Override de Streamlit kolom breedte DIRECT in de weergave
                    st.markdown("""<style>[data-testid="column"] { display: block !important; width: 31% !important; flex: 1 1 31% !important; }</style>""", unsafe_allow_html=True)
                    
                    photo_name = st.session_state.my_cards[idx]
                    is_found = st.session_state.found[idx]
                    img_path = os.path.join(IMAGE_DIR, photo_name)
                    
                    try:
                        img_base64 = get_base64_image(img_path)
                        ext = photo_name.split('.')[-1]
                        status_class = "found" if is_found else ""
                        
                        # Toon de foto
                        st.markdown(f"""
                            <img src="data:image/{ext};base64,{img_base64}" 
                                 class="bingo-photo {status_class}">
                            """, unsafe_allow_html=True)
                        
                        # De knop
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