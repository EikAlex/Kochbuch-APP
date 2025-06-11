from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from models import Vorrat, Zutat, Rezept, RezeptZutat
import streamlit as st

# DB-Konfig aus Umgebungsvariablen
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "example")
DB_HOST = os.getenv("DB_HOST", "db:5432")
DB_NAME = os.getenv("POSTGRES_DB", "cooking_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Engine & Session-Factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def add_zutat_to_vorrat(db, name, einheit, menge, haltbar_bis, mindestbestand):
    # Zutat suchen oder neu anlegen
    zutat = db.query(Zutat).filter(Zutat.name == name).first()

    if not zutat:
        # Zutat existiert nicht, also anlegen
        zutat = Zutat(name=name, einheit=einheit)
        db.add(zutat)
        db.commit()  # Sicherstellen, dass Zutat gespeichert wird
        zutat = db.query(Zutat).filter(Zutat.name == name).first()
        st.write(zutat.einheit)
    # Prüfen, ob bereits ein Vorratseintrag für diese Zutat und dieses Haltbarkeitsdatum existiert
    vorratseintrag = db.query(Vorrat).filter(
        Vorrat.zutat_id == zutat.id, Vorrat.haltbar_bis == haltbar_bis
    ).first()

    if vorratseintrag:
        # Wenn Eintrag vorhanden ist, die Menge addieren
        vorratseintrag.menge_vorhanden += menge
        db.commit()  # Änderungen speichern
        st.success(
            f"✅ Menge für {name} wurde um {menge} erhöht. Neuer Vorrat: {vorratseintrag.menge_vorhanden} {einheit}.")
    else:
        # Wenn kein Eintrag vorhanden ist, neuen Vorratseintrag erstellen
        eintrag = Vorrat(
            zutat_id=zutat.id,
            menge_vorhanden=menge,
            haltbar_bis=haltbar_bis,
            mindestbestand=mindestbestand
        )
        db.add(eintrag)
        db.commit()  # Sicherstellen, dass der Vorratseintrag gespeichert wird
        st.success(f"✅ {name} wurde zum Vorrat hinzugefügt!")


def delete_vorratseintrag(db, vorrat_id: int):
    # Löscht einen Vorratseintrag aus der Datenbank.
    eintrag = db.query(Vorrat).filter(Vorrat.id == vorrat_id).first()
    if eintrag:
        db.delete(eintrag)
        db.commit()


def delete_zutat_from_db(db, zutat_name):
    # Löscht eine Zutat aus der Datenbank.
    zutat = db.query(Zutat).filter(Zutat.name == zutat_name).first()
    if zutat:
        db.delete(zutat)
        db.commit()
        return True
    return False


# def add_rezept(db, name, beschreibung, zutaten_liste):
#     # Rezept anlegen
#     rezept = Rezept(name=name, beschreibung=beschreibung)
#     db.add(rezept)
#     db.commit()
#     db.refresh(rezept)

#     for zutat_id, menge in zutaten_liste:
#         rz = RezeptZutat(rezept_id=rezept.id, zutat_id=zutat_id, menge=menge)
#         db.add(rz)

#    db.commit()
def add_rezept(db, name, beschreibung, zutaten_liste):
    # Neues Rezept erstellen
    rezept = Rezept(name=name, beschreibung=beschreibung)
    db.add(rezept)
    db.flush()  # Holt die ID des Rezepts vor dem Commit

    for zutat_id, menge_pro_portion in zutaten_liste:
        rezept_zutat = RezeptZutat(
            rezept_id=rezept.id,
            zutat_id=zutat_id,
            menge=menge_pro_portion  # wichtig: nur pro Portion speichern!
        )
        db.add(rezept_zutat)

    db.commit()