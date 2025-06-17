from datetime import datetime
from shared.db_models import Vorrat, Zutat, Rezept, RezeptZutat

# Liste mit Standard-Einheiten
defaul_einheit = [
    "g", "ml", "Stück", "TL", "EL", "Prise", "kg", "l", "Pck.", "Dose", "Glas"]


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


def check_haltbarkeit(ablaufdatum):
    """
    Gibt einen farblich markierten HTML-String mit passendem Symbol je nach Haltbarkeit zurück.
    """
    heute = heute = datetime.today().date()
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
