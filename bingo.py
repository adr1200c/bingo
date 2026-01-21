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
    .block-container { padding: 10px !important; max-width: 400px !important; }
    
    /* Het Grid: forceert 3 kolommen, zelfs op de kleinste schermen */
    .bingo-grid {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
    }

    /* Het klikbare vakje */
    .bingo-item {
        width: 100%;
        aspect-ratio: 1 / 1;
        position: relative;
        cursor: pointer;
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
        border: 3px solid #4CAF50 !important;
    }

    /* Verberg de standaard knoppen die we nu niet meer nodig hebben voor het grid */
    .stButton button { width: 100%; }
    
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

        # 3. Bouw het grid in één HTML blok
        # We maken een grote string met alle HTML
        grid_html = '<div class="bingo-grid">'
        
        for i in range(9):
            photo_name = st.session_state.my_cards[i]
            is_found = st.session_state.found[i]
            img_path = os.path.join(IMAGE_DIR, photo_name)
            
            try:
                img_b64 = get_base64_image(img_path)
                ext = photo_name.split('.')[-1]
                status_class = "found" if is_found else ""
                
                # Elke foto wordt een link die een 'trigger' verstuurt naar Streamlit
                grid_html += f'''
                    <div class="bingo-item">
                        <img src="data:image/{ext};base64,{img_b64}" class="bingo-photo {status_class}">
                    </div>
                '''
            except:
                grid_html += '<div class="bingo-item" style="background:#eee;">err</div>'
        
        grid_html += '</div>'
        
        # Toon de volledige tabel
        st.markdown(grid_html, unsafe_allow_html=True)

        # Omdat we in pure HTML geen klik-events naar Python kunnen sturen zonder 
        # ingewikkelde componenten, gebruiken we hieronder simpele knoppen 
        # om de status per nummer bij te werken.
        st.write("Tik op het nummer om af te strepen:")
        cols = st.columns(9)
        for i in range(9):
            with cols[i]:
                label = "✅" if st.session_state.found[i] else str(i+1)
                if st.button(label, key=f"check_{i}"):
                    st.session_state.found[i] = not st.session_state.found[i]
                    st.rerun()

        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()