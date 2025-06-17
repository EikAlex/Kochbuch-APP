from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from shared.config import DATABASE_URL  # Zentrale Konfiguration
from db_models.base import Base, Zutat, Vorrat, Rezept, RezeptZutat
from util import initialize_default_zutaten
from datetime import date
from config import DATABASE_URL


engine = create_engine(DATABASE_URL, connect_args={
                       "check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
############################################################################
# Testdaten / Rezept mit Zutaten anlegen
# if True:
#     try:
#         # Zutaten anlegen, aber nur, wenn sie noch nicht existieren
#         zutaten_namen = ["Mehl", "Ei", "Milch", "Zucker"]
#         zutaten_einheiten = ["g", "Stück", "ml", "g"]
        
#         zutaten = []
#         for name, einheit in zip(zutaten_namen, zutaten_einheiten):
#             # Prüfe, ob die Zutat bereits existiert
#             existing_zutat = db.query(Zutat).filter(Zutat.name == name).first()
#             if not existing_zutat:
#                 # Zutat hinzufügen, wenn sie nicht existiert
#                 zutat = Zutat(name=name, einheit=einheit)
#                 db.add(zutat)
#                 zutaten.append(zutat)
#             else:
#                 zutaten.append(existing_zutat)

#         db.commit()

#         # Vorrat anlegen
#         vorrat_daten = [
#             (zutaten[0].id, 1000, date(2025, 12, 31), 200),  # Mehl
#             (zutaten[1].id, 6, date(2025, 5, 1), 2),      # Ei
#             (zutaten[2].id, 500, date(2025, 5, 3), 200),    # Milch
#             (zutaten[3].id, 300, date(2026, 1, 1), 500),    # Zucker
#         ]

#         for zutat_id, menge, haltbar_bis, mindest in vorrat_daten:
#             # Prüfe, ob der Vorrat mit dieser Zutat und Haltbarkeit bereits existiert
#             existing_vorrat = db.query(Vorrat).filter(
#                 Vorrat.zutat_id == zutat_id,
#                 Vorrat.haltbar_bis == haltbar_bis,
#                 Vorrat.mindestbestand == mindest
#             ).first()
#             if not existing_vorrat:
#                 db.add(Vorrat(zutat_id=zutat_id, menge_vorhanden=menge, haltbar_bis=haltbar_bis))

#         db.commit()

#         # Rezept anlegen
#         rezept = Rezept(name="Pfannkuchen", beschreibung="Mehl, Eier, Milch und Salz in eine Schüssel geben. Für süße Pfannkuchen etwas Zucker dazugeben. Alles zu einem glatten Teig verrühren. Wenn der Teig zu dick ist, etwas mehr Milch dazugeben. Eine Pfanne erhitzen und mit etwas Butter oder Öl einfetten. Eine Kelle Teig in die heiße Pfanne geben und gleichmäßig verteilen. Von beiden Seiten goldbraun backen. Nach Belieben servieren – zum Beispiel mit Apfelmus, Marmelade, Zimt und Zucker oder herzhaft gefüllt.")
#         db.add(rezept)
#         db.commit()

#         # Zutaten mit Mengen für das Rezept
#         rezept_zutaten = [
#             (rezept.id, zutaten[0].id, 200),  # Mehl
#             (rezept.id, zutaten[1].id, 2),    # Ei
#             (rezept.id, zutaten[2].id, 250),  # Milch
#             (rezept.id, zutaten[3].id, 50),   # Zucker
#         ]

#         for rezept_id, zutat_id, menge in rezept_zutaten:
#             # Überprüfe, ob die Kombination Rezept und Zutat bereits existiert
#             existing_rezept_zutat = db.query(RezeptZutat).filter(
#                 RezeptZutat.rezept_id == rezept_id,
#                 RezeptZutat.zutat_id == zutat_id
#             ).first()
#             if not existing_rezept_zutat:
#                 db.add(RezeptZutat(rezept_id=rezept_id, zutat_id=zutat_id, menge=menge))

#         db.commit()

#         print("✅ Testdaten erfolgreich hinzugefügt.")

#     except IntegrityError as e:
#         # Hier fängt man die Exception ab, falls ein Duplikat-Fehler auftritt
#         db.rollback()  # Transaktion zurückrollen, falls Fehler auftreten
#         print(f"❌ Fehler beim Hinzufügen der Testdaten: {e}")
############################################################################

# Initialisiere Standard-Zutaten
# initialize_default_zutaten(db)

# # Schließen der Session
# db.close()