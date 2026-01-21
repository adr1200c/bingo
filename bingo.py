import streamlit as st
import random
import os

# Pagina instellingen
st.set_page_config(page_title="Familie Foto Bingo", layout="wide")

st.title("📸 Onze Familie Foto Bingo")
st.write("Tik op de foto's die je voorbij hoort komen in het verhaal!")

# Map waar je foto's staan (zorg dat deze in dezelfde map als je script staat)
IMAGE_DIR = "familie_fotos"

# Haal alle bestanden uit de map op
if not os.path.exists(IMAGE_DIR):
    st.error(f"Map '{IMAGE_DIR}' niet gevonden. Maak deze map aan en zet je foto's erin.")
else:
    all_photos = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('png', 'jpg', 'jpeg'))]

    if len(all_photos) < 9:
        st.warning("Zorg voor minstens 9 foto's in de map!")
    else:
        # Kies 9 random foto's en sla ze op in de 'session state' zodat ze niet veranderen bij elke klik
        if 'my_cards' not in st.session_state:
            st.session_state.my_cards = random.sample(all_photos, 9)
            st.session_state.found = [False] * 9

        # Maak een 3x3 grid
        cols = st.columns(3)

        for i in range(9):
            with cols[i % 3]:
                photo_name = st.session_state.my_cards[i]
                is_found = st.session_state.found[i]
                
                # Toon de foto
                img_path = os.path.join(IMAGE_DIR, photo_name)
                
                # Visuele feedback als er geklikt is
                label = "✅ GEVONDEN" if is_found else "Vink af"
                
                if st.button(label, key=f"btn_{i}"):
                    st.session_state.found[i] = not st.session_state.found[i]
                    st.rerun()
                
                if is_found:
                    # Grijze/transparante versie als gevonden
                    st.image(img_path, use_container_width=True, caption=photo_name, channels="RGB")
                else:
                    st.image(img_path, use_container_width=True, caption=photo_name)

        # Check voor Bingo
        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO! Je hebt de hele kaart vol!")

if st.button("Nieuwe kaart genereren"):
    del st.session_state.my_cards
    st.rerun()