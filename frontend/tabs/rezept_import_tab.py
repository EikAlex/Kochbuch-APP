import streamlit as st
import requests
from PIL import Image
import numpy as np
import easyocr
from bs4 import BeautifulSoup

API_IMPORT = "http://rezept-import_service:5005/api/extrahieren"


def render():
    st.subheader("📥 Rezept-Import")

    option = st.radio(
        "Was möchtest du importieren?",
        ("📷 Bild hochladen", "🌐 Webseite angeben")
    )

    extrahierter_text = ""

    if option == "📷 Bild hochladen":
        bild = st.file_uploader("Lade ein Bild hoch", type=["jpg", "jpeg", "png"])
        if bild:
            st.image(bild, caption="Hochgeladenes Bild", use_column_width=True)

            img = Image.open(bild)
            img_array = np.array(img)

            reader = easyocr.Reader(["de", "en"], gpu=False)
            with st.spinner("🔍 Texterkennung läuft..."):
                result = reader.readtext(img_array, detail=0, paragraph=True)

            extrahierter_text = "\n".join(result)
            st.text_area("📄 Erkannter Text:", extrahierter_text, height=300)

    elif option == "🌐 Webseite angeben":
        url = st.text_input("Gib die URL einer Rezept-Webseite ein")
        if url:
            try:
                st.info(f"🔗 Webseite wird geladen: {url}")
                page = requests.get(url, timeout=10)
                soup = BeautifulSoup(page.content, "html.parser")
                texte = [p.get_text(strip=True) for p in soup.find_all(["p", "li"])]
                extrahierter_text = "\n".join(texte)
                st.text_area("📄 Gefundener Text:", extrahierter_text, height=300)
            except Exception as e:
                st.error(f"❌ Fehler beim Laden der Seite: {e}")

    if extrahierter_text:
        if st.button("🤖 Rezept aus Text extrahieren"):
            with st.spinner("🧠 LLM wird kontaktiert..."):
                try:
                    payload = {"text": extrahierter_text}
                    response = requests.post(API_IMPORT, json=payload)
                    if response.status_code == 200:
                        rezept_daten = response.json()
                        st.success("🎉 Text erfolgreich extrahiert!")

                        st.markdown("---")
                        with st.expander("🧾 Importiertes Rezept ansehen", expanded=True):
                            st.subheader(rezept_daten["name"])

                            st.markdown("### 📝 Beschreibung")
                            st.write(rezept_daten["beschreibung"])

                            st.markdown("### 🛒 Zutatenliste")
                            for z in rezept_daten["zutaten"]:
                                st.write(f"- {z['menge']} x {z['name']}")

                        st.markdown("---")
                        st.subheader("✏️ Nachbearbeiten (optional)")

                        rezeptname = st.text_input("Rezeptname", value=rezept_daten["name"], key="rezeptname_input")
                        beschreibung = st.text_area("Beschreibung", value=rezept_daten["beschreibung"], key="beschreibung_input")

                        edited_zutaten = []
                        st.markdown("### 🛒 Zutaten bearbeiten")
                        for i, z in enumerate(rezept_daten["zutaten"]):
                            col1, col2 = st.columns([3, 1])
                            key_suffix = f"{i}"
                            name = col1.text_input(f"Zutat {i+1} Name", value=z["name"], key=f"edit_name_{key_suffix}")
                            menge = col2.number_input(f"Menge {i+1}", value=z["menge"], min_value=0.0, step=1.0, key=f"edit_menge_{key_suffix}")
                            edited_zutaten.append({"name": name, "menge": menge})

                        if st.button("✅ Bearbeitete Version speichern"):
                            try:
                                neues_rezept = {
                                    "name": rezeptname,
                                    "beschreibung": beschreibung,
                                    "zutaten": edited_zutaten
                                }
                                # Hier könnte ein weiterer API-Call zum Speichern des bearbeiteten Rezepts erfolgen
                                st.success(f"🎉 Rezept '{rezeptname}' erfolgreich gespeichert!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Fehler beim Speichern: {e}")

                        st.markdown("---")
                        if st.button("📖 Importiertes Rezept in Übersicht anzeigen"):
                            st.session_state.rezept_phase = "start"
                            st.rerun()
                    else:
                        st.error(f"❌ Fehler beim LLM-Import: {response.text}")
                except Exception as e:
                    st.error(f"❌ Fehler beim LLM-Import: {e}")
