import streamlit as st
import requests

API_BASE = "http://rezept_service:5002/api/rezepte"
ZUTATEN_API = "http://vorrat_service:5001/api/zutaten"


def render():
    st.subheader("📥 Neues Rezept hinzufügen")

    if "rezept_phase" not in st.session_state:
        st.session_state.rezept_phase = "start"
    if "rezept_zutaten_liste" not in st.session_state:
        st.session_state.rezept_zutaten_liste = []

    if st.session_state.rezept_phase == "start":
        with st.form("rezept_start_form"):
            rezeptname = st.text_input("Rezeptname")
            beschreibung = st.text_area("Beschreibung")
            portionen = st.number_input(
                "Anzahl Portionen", min_value=1, value=1, step=1)
            weiter = st.form_submit_button("➡️ Zutaten wählen")

            if weiter and rezeptname and portionen:
                st.session_state.rezeptname = rezeptname
                st.session_state.beschreibung = beschreibung
                st.session_state.portionen = portionen
                st.session_state.rezept_phase = "zutaten"
                st.rerun()

    elif st.session_state.rezept_phase == "zutaten":
        st.markdown(
            f"**Rezept:** {st.session_state.rezeptname} für {st.session_state.portionen} Portion(en)")

        try:
            zutaten_response = requests.get(f"{ZUTATEN_API}").json()
            zutaten_ids = [z['id'] for z in zutaten_response]
            zutaten_namen = [
                f"{z['name']} ({z['einheit']})" for z in zutaten_response]
        except:
            zutaten_ids = []
            zutaten_namen = []

        with st.form("zutat_hinzufuegen_form"):
            zutat_id = st.selectbox("Zutat auswählen", zutaten_ids,
                                    format_func=lambda x: zutaten_namen[zutaten_ids.index(x)])
            menge = st.number_input(
                "Menge für **1 Portion**", min_value=0.0, step=0.1)
            hinzufuegen = st.form_submit_button("➕ Zutat hinzufügen")

            if hinzufuegen and menge > 0:
                st.session_state.rezept_zutaten_liste.append({
                    "zutat_id": zutat_id,
                    "menge_pro_portion": menge
                })
                st.rerun()

        st.subheader("🧾 Zutatenliste")
        if st.session_state.rezept_zutaten_liste:
            for i, eintrag in enumerate(st.session_state.rezept_zutaten_liste):
                z = zutaten_response[zutaten_ids.index(eintrag["zutat_id"])]
                gesamtmenge = eintrag["menge_pro_portion"] * \
                    st.session_state.portionen
                col1, col2, col3, col4 = st.columns([4, 2, 3, 1])
                col1.write(z["name"])
                col2.write(
                    f"{eintrag['menge_pro_portion']} {z['einheit']} pro Portion")
                col3.write(f"{gesamtmenge} {z['einheit']} gesamt")
                if col4.button("❌", key=f"del_zutat_{i}"):
                    st.session_state.rezept_zutaten_liste.pop(i)
                    st.rerun()
        else:
            st.info("Noch keine Zutat hinzugefügt.")

    if st.session_state.rezept_zutaten_liste:
        if st.button("✅ Rezept speichern"):
            zutaten_payload = [
                {
                    "zutat_id": e["zutat_id"],
                    "menge": e["menge_pro_portion"] * st.session_state.portionen
                } for e in st.session_state.rezept_zutaten_liste
            ]
            payload = {
                "name": st.session_state.rezeptname,
                "beschreibung": st.session_state.beschreibung,
                "zutaten": zutaten_payload
            }
            res = requests.post(API_BASE, json=payload)
            if res.status_code == 200:
                st.success("🎉 Rezept gespeichert!")
                st.session_state.rezept_phase = "start"
                st.session_state.rezept_zutaten_liste = []
                st.rerun()
            else:
                st.error(f"Fehler: {res.text}")

    st.divider()
    st.subheader("📖 Deine Rezepte")

    rezepte = requests.get(API_BASE).json()
    for i, rezept in enumerate(rezepte):
        with st.expander(rezept["name"]):
            st.markdown(rezept.get("beschreibung") or "_Keine Beschreibung_")
            portionen_input = st.number_input(
                f"👨‍🍳 Wie viele Portionen möchtest du kochen?",
                min_value=1, value=1, step=1, key=f"portionen_{rezept['id']}"
            )

            st.markdown("**Zutaten:**")
            for rz in rezept["zutaten"]:
                berechnete_menge = rz["menge"] * portionen_input
                st.write(
                    f"- {berechnete_menge} {rz['einheit']} {rz['zutat_name']}")

            if st.button("🗑️ Löschen", key=f"delete_{rezept['id']}_{i}"):
                res = requests.delete(f"{API_BASE}/{rezept['id']}")
                if res.status_code == 200:
                    st.success(f"✅ Rezept '{rezept['name']}' gelöscht!")
                    st.rerun()
                else:
                    st.error(f"❌ Fehler beim Löschen: {res.text}")
