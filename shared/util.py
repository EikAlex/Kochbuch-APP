from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from shared.db_models import Vorrat, Zutat, Rezept, RezeptZutat
from sqlalchemy.exc import IntegrityError
from datetime import date

def initialize_default_zutaten(db):
    # Liste mit Standard-Zutaten und ihren Einheiten (Name, Einheit)
    default_zutaten_mit_einheit = [
        ("Tomaten", "Stück"), ("Kartoffeln", "g"), ("Zwiebeln", "Stück"), ("Knoblauch", "Stück"),
        ("Salz", "g"), ("Pfeffer", "g"), ("Olivenöl", "ml"), ("Mehl", "g"),
        ("Eier", "Stück"), ("Milch", "ml"), ("Butter", "g"), ("Hefe", "g"),
        ("Paprika", "Stück"), ("Kräuter", "g"), ("Zucker", "g"), ("Reis", "g"),
        ("Pasta", "g"), ("Linsen", "g"), ("Hähnchenbrust", "g"), ("Rindfleisch", "g"),
        ("Schinken", "g"), ("Mozzarella", "g"), ("Parmesan", "g"), ("Sahne", "ml"),
        ("Kochschinken", "g"), ("Paprikapulver", "g"), ("Chili", "Stück"), ("Kaffee", "g"),
        ("Kakaopulver", "g"), ("Honig", "ml"), ("Essig", "ml"), ("Senf", "ml"),
        ("Balsamico", "ml"), ("Kokosmilch", "ml"), ("Gemüsebrühe", "ml"), ("Fisch", "g"),
        ("Thunfisch", "g"), ("Spinat", "g"), ("Lauch", "Stück"), ("Karotten", "Stück")
    ]
    # Überprüfen, ob jede Zutat bereits existiert und hinzufügen, falls nicht
    for zutat_name, zutat_einheit in default_zutaten_mit_einheit:
        # Überprüfen, ob die Zutat schon in der DB existiert
        zutat = db.query(Zutat).filter(Zutat.name == zutat_name).first()
        if not zutat:
            # Wenn die Zutat nicht existiert, fügen wir sie hinzu
            # Stellen Sie sicher, dass das Zutat-Modell ein 'einheit'-Feld hat
            new_zutat = Zutat(name=zutat_name, einheit=zutat_einheit)
            db.add(new_zutat)
            # Es ist effizienter, commit() außerhalb der Schleife aufzurufen
            # db.commit()
            # db.refresh(new_zutat)
            print(f"Zutat '{zutat_name}' mit Einheit '{zutat_einheit}' wird hinzugefügt.")
        else:
            print(f"Zutat '{zutat_name}' ist bereits vorhanden.")
            # Optional: Überprüfen und aktualisieren Sie die Einheit, falls sie fehlt oder falsch ist
            if not zutat.einheit:
                 zutat.einheit = zutat_einheit
                 print(f"Einheit für '{zutat_name}' auf '{zutat_einheit}' aktualisiert.")
            elif zutat.einheit != zutat_einheit:
                 print(f"Hinweis: Vorhandene Einheit '{zutat.einheit}' für '{zutat_name}' unterscheidet sich von Standard '{zutat_einheit}'.")


    # Einmaliges Commit am Ende, nachdem alle potenziellen neuen Zutaten hinzugefügt wurden
    try:
        db.commit()
        print("Alle neuen Zutaten erfolgreich hinzugefügt und Änderungen committet.")
    except Exception as e:
        db.rollback() # Änderungen rückgängig machen im Fehlerfall
        print(f"Fehler beim Committen der Änderungen: {e}")

############################################################################
# Testdaten / Rezept mit Zutaten anlegen
def initialize_test_rezept(db):
    if True:
        try:
            # Zutaten anlegen, aber nur, wenn sie noch nicht existieren
            zutaten_namen = ["Mehl", "Ei", "Milch", "Zucker"]
            zutaten_einheiten = ["g", "Stück", "ml", "g"]
            
            zutaten = []
            for name, einheit in zip(zutaten_namen, zutaten_einheiten):
                # Prüfe, ob die Zutat bereits existiert
                existing_zutat = db.query(Zutat).filter(Zutat.name == name).first()
                if not existing_zutat:
                    # Zutat hinzufügen, wenn sie nicht existiert
                    zutat = Zutat(name=name, einheit=einheit)
                    db.add(zutat)
                    zutaten.append(zutat)
                else:
                    zutaten.append(existing_zutat)

            db.commit()

            # Vorrat anlegen
            vorrat_daten = [
                (zutaten[0].id, 1000, date(2025, 12, 31), 200),  # Mehl
                (zutaten[1].id, 6, date(2025, 5, 1), 2),      # Ei
                (zutaten[2].id, 500, date(2025, 5, 3), 200),    # Milch
                (zutaten[3].id, 300, date(2026, 1, 1), 500),    # Zucker
            ]

            for zutat_id, menge, haltbar_bis, mindest in vorrat_daten:
                # Prüfe, ob der Vorrat mit dieser Zutat und Haltbarkeit bereits existiert
                existing_vorrat = db.query(Vorrat).filter(
                    Vorrat.zutat_id == zutat_id,
                    Vorrat.haltbar_bis == haltbar_bis,
                    Vorrat.mindestbestand == mindest
                ).first()
                if not existing_vorrat:
                    db.add(Vorrat(zutat_id=zutat_id, menge_vorhanden=menge, haltbar_bis=haltbar_bis))

            db.commit()

            # Rezept anlegen
            rezept = Rezept(name="Pfannkuchen", beschreibung="Mehl, Eier, Milch und Salz in eine Schüssel geben. Für süße Pfannkuchen etwas Zucker dazugeben. Alles zu einem glatten Teig verrühren. Wenn der Teig zu dick ist, etwas mehr Milch dazugeben. Eine Pfanne erhitzen und mit etwas Butter oder Öl einfetten. Eine Kelle Teig in die heiße Pfanne geben und gleichmäßig verteilen. Von beiden Seiten goldbraun backen. Nach Belieben servieren – zum Beispiel mit Apfelmus, Marmelade, Zimt und Zucker oder herzhaft gefüllt.")
            db.add(rezept)
            db.commit()

            # Zutaten mit Mengen für das Rezept
            rezept_zutaten = [
                (rezept.id, zutaten[0].id, 200),  # Mehl
                (rezept.id, zutaten[1].id, 2),    # Ei
                (rezept.id, zutaten[2].id, 250),  # Milch
                (rezept.id, zutaten[3].id, 50),   # Zucker
            ]

            for rezept_id, zutat_id, menge in rezept_zutaten:
                # Überprüfe, ob die Kombination Rezept und Zutat bereits existiert
                existing_rezept_zutat = db.query(RezeptZutat).filter(
                    RezeptZutat.rezept_id == rezept_id,
                    RezeptZutat.zutat_id == zutat_id
                ).first()
                if not existing_rezept_zutat:
                    db.add(RezeptZutat(rezept_id=rezept_id, zutat_id=zutat_id, menge=menge))

            db.commit()

            print("✅ Testdaten erfolgreich hinzugefügt.")

        except IntegrityError as e:
            # Hier fängt man die Exception ab, falls ein Duplikat-Fehler auftritt
            db.rollback()  # Transaktion zurückrollen, falls Fehler auftreten
            print(f"❌ Fehler beim Hinzufügen der Testdaten: {e}")


def check_haltbarkeit(ablaufdatum):
    """
    Returns a color-coded HTML string with a symbol based on expiration date.
    """
    heute = datetime.today().date()
    tage_bis_ablauf = (ablaufdatum - heute).days

    if tage_bis_ablauf < 0:
        farbe = "red"
        symbol = "⚠️"
    elif tage_bis_ablauf <= 3:
        farbe = "orange"
        symbol = "⏳"
    else:
        farbe = "green"
        symbol = ""
    ablaufdatum = ablaufdatum.strftime("%d.%m.%Y")
    return f'<span style="color:{farbe}; font-size:18px;">{symbol} 📅 {ablaufdatum}</span>'
