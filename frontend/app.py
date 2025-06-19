import streamlit as st
from tabs import vorschlag_tab, vorrat_tab, rezepte_tab, einkaufsliste_tab, rezept_import_tab


st.set_page_config(page_title="Kochbuch", layout="wide")
st.title("🥘 Digitale Kochbuch-App")

# Tabs für die verschiedenen Funktionen
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📦 Vorrat", "📖 Rezepte", "🧠 Vorschläge", "🛒 Einkaufsliste", "📥 Rezept-Import"])

with tab1:
    vorrat_tab.render()

with tab2:
    rezepte_tab.render()

with tab3:
    vorschlag_tab.render()

with tab4:
    einkaufsliste_tab.render()

with tab5:
    rezept_import_tab.render()
