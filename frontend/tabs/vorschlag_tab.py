import streamlit as st
import requests

API_URL = "http://localhost:5003/api/vorschlaege"


def render():
    st.subheader("🧠 Rezeptvorschläge basierend auf deinem Vorrat")

    # REST-basierte Vorschläge abrufen
    try:
        vorschlaege = requests.get(API_URL).json()

        if not vorschlaege:
            st.info("Keine Rezepte gefunden.")
            return

        for rezept in vorschlaege:
            with st.expander(rezept["rezept"]):
                if rezept["portionen_moeglich"] >= 1:
                    st.success(
                        f"✅ Du kannst ca. {rezept['portionen_moeglich']} Portion(en) kochen")
                else:
                    st.warning(
                        "⚠️ Du hast nicht genug Vorrat für eine Portion.")

                if rezept.get("fehlende"):
                    st.markdown("**Fehlende Zutaten:**")
                    for fehl in rezept["fehlende"]:
                        st.write(
                            f"- {fehl['fehlt']:.2f} {fehl['einheit']} {fehl['name']}")

                if rezept.get("zutaten"):
                    st.markdown("**Zutatenübersicht pro Portion:**")
                    for z in rezept["zutaten"]:
                        st.write(
                            f"- {z['menge']} {z['einheit']} {z['name']} --  (🧺 Vorrat: {z['vorrat']} {z['einheit']})")

    except Exception as e:
        st.error(f"❌ Fehler beim Abrufen der Vorschläge: {e}")
