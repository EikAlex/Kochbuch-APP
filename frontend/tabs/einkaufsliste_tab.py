import streamlit as st
import requests

API_URL = "http://localhost:5004/api/einkaufsliste"
ZUTATEN_API = "http://localhost:5001/api/zutaten"
AUTO_URL = f"{API_URL}/auto"
KAUFEN_ENDPOINT = lambda eid: f"{API_URL}/{eid}/kaufen"


def render():
    st.subheader("🛒 Einkaufsliste erstellen und verwalten")

    # Auto-Auffüllen basierend auf Mindestbestand
    if st.button("🔄 Automatisch ergänzen bei Mindestbestand"):
        try:
            res = requests.post(AUTO_URL)
            if res.ok:
                result = res.json()
                hinzu = result.get("hinzugefuegt", 0)
                if hinzu > 0:
                    st.success(f"🧠 {hinzu} Zutaten wurden automatisch ergänzt.")
                else:
                    st.info("📦 Alles im Soll – kein Nachkauf notwendig.")
                st.rerun()
            else:
                st.error(f"Fehler: {res.text}")
        except Exception as e:
            st.error(f"Fehler beim Auto-Auffüllen: {e}")

    st.markdown("---")
    with st.expander("➕ Zutat zur Einkaufsliste hinzufügen"):
        try:
            zutaten = requests.get(ZUTATEN_API).json()
            name_to_id = {z["name"]: z["id"] for z in zutaten}
            auswahl = st.selectbox("Zutat auswählen", list(name_to_id.keys()), key="zutat_einkauf")
            menge = st.number_input("Menge", min_value=1, step=1, key="menge_einkauf")

            if st.button("🛒 Zur Einkaufsliste hinzufügen", key="hinzufuegen_einkauf"):
                payload = {"zutat_id": name_to_id[auswahl], "menge": menge}
                res = requests.post(API_URL, json=payload)
                if res.ok:
                    st.success("Hinzugefügt!")
                    st.rerun()
                else:
                    st.error(f"Fehler: {res.text}")
        except Exception as e:
            st.error(f"Fehler beim Laden der Zutaten: {e}")

    st.markdown("---")
    st.subheader("📋 Aktuelle Einkaufsliste")

    try:
        eintraege = requests.get(API_URL).json()

        if eintraege:
            for eintrag in eintraege:
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                key_input = f"menge_input_{eintrag['id']}"

                col1.write(f"**{eintrag['zutat']}**")
                neue_menge = col2.number_input(
                    "",
                    min_value=0,
                    step=1,
                    value=int(eintrag["menge"]),
                    key=key_input,
                    label_visibility="collapsed"
                )

                if col3.button("💾", key=f"save_{eintrag['id']}"):
                    payload = {"menge": neue_menge}  # angepasste Payload
                    res = requests.put(f"{API_URL}/{eintrag['id']}", json=payload)
                    if res.ok:
                        st.success(f"Menge von '{eintrag['zutat']}' aktualisiert!")
                        st.rerun()
                    else:
                        st.error(f"Fehler: {res.text}")

                if col4.button("🛍️", key=f"bought_{eintrag['id']}"):
                    res = requests.post(KAUFEN_ENDPOINT(eintrag["id"]))
                    if res.ok:
                        st.success(f"'{eintrag['zutat']}' als gekauft markiert und in Vorrat übertragen!")
                        st.rerun()
                    else:
                        st.error(f"Fehler: {res.text}")

                if col5.button("❌", key=f"remove_{eintrag['id']}"):
                    res = requests.delete(f"{API_URL}/{eintrag['id']}")
                    if res.ok:
                        st.success(f"'{eintrag['zutat']}' wurde entfernt.")
                        st.rerun()
                    else:
                        st.error(f"Fehler: {res.text}")
        else:
            st.info("🧺 Deine Einkaufsliste ist aktuell leer.")

    except Exception as e:
        st.error(f"Fehler beim Laden der Einkaufsliste: {e}")
