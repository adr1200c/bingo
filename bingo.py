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

# 3. CSS om de tabel en knoppen te temmen
st.markdown("""
    <style>
    .block-container {
        padding: 10px !important;
        max-width: 500px !important;
    }
    
    /* De Tabel Forceer-methode */
    table {
        width: 100% !important;
        border-collapse: collapse;
        table-layout: fixed; /* Dwingt gelijke kolommen */
    }
    
    td {
        padding: 4px !important;
        vertical-align: top;
        width: 33.33%;
    }

    .bingo-photo {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        object-fit: cover !important;
        border-radius: 8px;
        border: 1px solid #ddd;
    }

    .found {
        filter: grayscale(100%) opacity(0.3);
        border: 3px solid #4CAF50 !important;
    }

    /* Streamlit knoppen binnen de tabelcellen */
    div.stButton > button {
        width: 100% !important;
        height: 30px !important;
        font-size: 10px !important;
        padding: 0px !important;
        margin-top: 2px !important;
    }
    
    h1 { text-align: center; font-size: 22px !important; }
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

        # 4. Het Grid bouwen met een HTML Tabel
        # We openen de tabel
        st.write('<table>', unsafe_allow_html=True)
        
        for row in range(3):
            cols = st.columns(3) # We gebruiken de kolommen alleen als anker voor de knoppen
            
            # We maken handmatig de rijen in de tabel
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
                        
                        # Toon de foto in de cel
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
        
        st.write('</table>', unsafe_allow_html=True)

        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()