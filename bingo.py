import streamlit as st
import random
import os
import base64

# 1. Pagina instellingen
st.set_page_config(page_title="Familie Bingo", layout="centered")

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

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

        # 2. De HTML & CSS voor het onbreekbare Grid
        # We bouwen een tabel die Safari NIET kan breken
        grid_html = """
        <style>
            .bingo-table {
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }
            .bingo-td {
                padding: 4px;
                text-align: center;
                width: 33.33%;
            }
            .bingo-img {
                width: 100%;
                aspect-ratio: 1 / 1;
                object-fit: cover;
                border-radius: 8px;
                border: 2px solid #ddd;
                display: block;
            }
            .found {
                filter: grayscale(100%) opacity(0.3);
                border: 2px solid #4CAF50;
            }
        </style>
        <table class="bingo-table">
            <tr>
        """

        for i in range(9):
            photo_name = st.session_state.my_cards[i]
            is_found = st.session_state.found[i]
            img_path = os.path.join(IMAGE_DIR, photo_name)
            
            try:
                img_b64 = get_base64_image(img_path)
                ext = photo_name.split('.')[-1]
                status_class = "found" if is_found else ""
                
                grid_html += f'''
                    <td class="bingo-td">
                        <img src="data:image/{ext};base64,{img_b64}" class="bingo-img {status_class}">
                        <div style="font-size:12px; margin-top:4px;">Foto {i+1}</div>
                    </td>
                '''
                
                if (i + 1) % 3 == 0 and i < 8:
                    grid_html += '</tr><tr>'
            except:
                grid_html += '<td class="bingo-td">⚠️</td>'

        grid_html += "</tr></table>"

        # 3. Render het Grid in één keer
        st.write("---")
        st.components.v1.html(grid_html, height=450) # Dit is de "muur" waar Safari niet doorheen komt
        st.write("---")

        # 4. De knoppen om af te vinken (in een compact grid eronder)
        st.write("Tik op de nummers die je hebt gevonden:")
        row1 = st.columns(3)
        row2 = st.columns(3)
        row3 = st.columns(3)
        all_cols = row1 + row2 + row3

        for i in range(9):
            with all_cols[i]:
                label = f"✅ {i+1}" if st.session_state.found[i] else f"Kies {i+1}"
                if st.button(label, key=f"btn_{i}"):
                    st.session_state.found[i] = not st.session_state.found[i]
                    st.rerun()

        if all(st.session_state.found):
            st.balloons()
            st.success("🎉 BINGO!")

st.divider()
if st.button("🔄 Nieuwe Kaart"):
    st.session_state.clear()
    st.rerun()