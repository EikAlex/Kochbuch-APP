import streamlit as st
import datetime
import requests
from shared.utils import check_haltbarkeit

API_BASE = "http://vorrat_service:5001/api/vorrat"
ZUTATEN_API = "http://vorrat_service:5001/api/zutaten"


def render():
    st.subheader("📥 Vorrat verwalten")

    action = st.radio("Wähle eine Aktion",
                      ("Zutat hinzufügen", "Zutat löschen"))

    if action == "Zutat hinzufügen":
        with st.form("vorrat_form"):
            try:
                response = requests.get(f"{ZUTATEN_API}/namen")
                response.raise_for_status()
                vorhandene_zutaten = response.json()
            except requests.exceptions.RequestException as e:
                st.error(f"Fehler beim Laden der Zutatennamen: {e}")
                vorhandene_zutaten = []
            except ValueError as e:  # Catch JSON decoding errors
                st.error(
                    f"Fehler beim Verarbeiten der Zutatennamen-Antwort: {e}")
                vorhandene_zutaten = []

            vorschlag = st.selectbox("Vorschlag wählen (optional)", [
                                     ""] + vorhandene_zutaten, index=0, key="vorschlag")

            name = st.text_input("Zutat eingeben", value=st.session_state.get(
                "vorschlag", ""), key="zutat_input")

            try:
                einheiten = requests.get(f"{ZUTATEN_API}/einheiten").json()
            except:
                einheiten = ["Stück", "g", "ml"]

            einheit = st.selectbox("Einheit", einheiten, key="einheit_input")
            menge = st.number_input(
                "Menge", min_value=1, step=1, key="menge_input")
            haltbar_bis = st.date_input(
                "Haltbar bis", value=datetime.date.today(), key="mhd_input")
            mindestbestand = st.number_input(
                "📜 Optional: Mindestbestand", min_value=0, step=1, value=0, key="mb_input")

            submitted = st.form_submit_button("Hinzufügen")

        if submitted:
            payload = {
                "name": name.strip().capitalize(),
                "menge": menge,
                "einheit": einheit,
                "haltbar_bis": haltbar_bis.isoformat(),
                "mindestbestand": mindestbestand
            }
            res = requests.post(API_BASE, json=payload)
            if res.status_code == 200:
                st.success(f"✅ {name} hinzugefügt oder aktualisiert!")
                st.rerun()
            else:
                st.error(f"❌ Fehler beim Hinzufügen: {res.text}")

    elif action == "Zutat löschen":
        st.subheader("🗑️ Zutat aus der Datenbank löschen")

        try:
            zutaten_liste = requests.get(f"{ZUTATEN_API}/namen").json()
        except:
            zutaten_liste = []

        zutat_to_delete = st.selectbox(
            "Wähle eine Zutat zum Löschen", zutaten_liste)

        if zutat_to_delete:
            if st.button(f"❌ {zutat_to_delete} löschen"):
                res = requests.delete(f"{ZUTATEN_API}/{zutat_to_delete}")
                if res.status_code == 200:
                    st.success(f"✅ Zutat '{zutat_to_delete}' wurde gelöscht!")
                    st.rerun()
                else:
                    st.error(f"❌ Fehler beim Löschen: {res.text}")

    st.divider()
    st.subheader("📦 Dein aktueller Vorrat")

    try:
        response = requests.get(API_BASE)
        response.raise_for_status()
        eintraege = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Abrufen der Vorratsdaten: {e}")
        eintraege = []
    except ValueError as e:
        st.error(f"Fehler beim Verarbeiten der API-Antwort: {e}")
        eintraege = []

    if eintraege:
        for eintrag in eintraege:
            col1, col2, col3, col4 = st.columns([3, 4, 2, 1])

            col1.write(f"**{eintrag['name']}**")
            menge_text = f"{eintrag['menge']} {eintrag['einheit']}"

            if eintrag.get("mindestbestand") and eintrag["menge"] < eintrag["mindestbestand"]:
                menge_text += f" 🔴 (unter Mindestbestand: {eintrag['mindestbestand']} {eintrag['einheit']})"

            col2.write(menge_text)

            haltbar_bis_value = eintrag.get("haltbar_bis")
            if haltbar_bis_value:
                try:
                    haltbar_bis_date = datetime.date.fromisoformat(haltbar_bis_value)
                    col3.markdown(check_haltbarkeit(haltbar_bis_date), unsafe_allow_html=True)
                except ValueError:
                    col3.write("Ungültiges Datum")
            else:
                col3.write("-")

            if col4.button("🗑️", key=f"delete_{eintrag['id']}"):
                requests.delete(f"{API_BASE}/{eintrag['id']}")
                st.success(f"✅ {eintrag['name']} wurde gelöscht!")
                st.rerun()
    else:
        st.info("Noch nichts im Vorrat.")

    try:
        response = requests.get(ZUTATEN_API, timeout=10)
        response.raise_for_status()
        zutaten_response = response.json()
        if not zutaten_response:
            st.warning("Keine Zutaten gefunden.")
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Abrufen der Zutaten: {e}")
        zutaten_response = []
