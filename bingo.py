import streamlit as st
import random
import os
import base64

st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 1. CSS die het "springen" naar grote foto's verbiedt
st.markdown("""
    <style>
    /* Forceer de hoofdcontainer om smal te blijven en niet te verspringen */
    .block-container {
        max-width: 400px !important;
        padding: 5px !important;
    }

    /* HET ONBREEKBARE GRID */
    .bingo-grid {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important; /* ALTIJD 3 kolommen */
        gap: 8px !important;
        width: 100% !important;
    }

    .bingo-cell {
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
        border: 2px solid #eee;
    }

    .found {
        filter: grayscale(100%) opacity(0.3);
        border: 2px solid #4CAF50 !important;
    }

    /* Dwing Streamlit kolommen (als ze toch laden) om klein te blijven */
    [data-testid="column"] {
        width: 33% !important;
        flex: 0 0 33% !important;
        min-width: 33% !important;
    }
    
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important; /* Verbiedt het onder elkaar klappen */
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

        # 2. De Bingo Kaart bouwen
        # We gebruiken GEEN st.columns(3) direct in een loop, maar dwingen de structuur
        for row in range(3):
            # De 'nowrap' in de CSS zorgt dat deze 3 kolommen naast elkaar BLIJVEN
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
                        
                        # Toon foto
                        st.markdown(f'''<img src="data:image/{ext};base64,{img_b64}" class="bingo-photo {status_class}">''', unsafe_allow_html=True)
                        
                        # Toon knop
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