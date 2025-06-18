import streamlit as st
from tabs import vorschlag_tab, vorrat_tab, rezepte_tab, einkaufsliste_tab, rezept_import_tab
from sqlalchemy.orm import Session
from shared.database import SessionLocal, engine
from shared.db_models import Base
from shared.util import initialize_default_zutaten, initialize_test_rezept


def run_initial_setup():
    """
    Initializes the database with default and test data.
    Ensures no duplicates are added.
    """
    db: Session = SessionLocal()
    try:
        # Ensure all tables are created
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created.")

        # Initialize default and test data
        initialize_default_zutaten(db)
        initialize_test_rezept(db)
        print("Default and test data initialized.")
    except Exception as e:
        print(f"Error during initial setup: {e}")
        if db:
            db.rollback()
    finally:
        if db:
            db.close()
        print("Initial setup routine finished.")


# Run the setup at the very beginning of the app's execution
run_initial_setup()

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
