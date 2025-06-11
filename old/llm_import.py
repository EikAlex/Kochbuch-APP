from openai import OpenAI
import json
from models import Rezept, RezeptZutat, Zutat
from sqlalchemy.orm import Session
import streamlit as st

# System-Prompt für saubere Extraktion
system_prompt = """
Du bist ein Rezept-Extraktionsassistent. 
Formatiere den folgenden Text in gültiges JSON-Format:

{
  "name": "Rezeptname",
  "beschreibung": "Zubereitung",
  "zutaten": [
    {"name": "Mehl", "menge": 200},
    {"name": "Ei", "menge": 2}
  ]
}

Antwort bitte ausschließlich im JSON-Format, ohne zusätzliche Kommentare oder Erklärungen.
"""

# Rezept aus Text extrahieren
def rezept_aus_text_extrahieren(text: str) -> dict:
    client = OpenAI(api_key=st.secrets["openai"]["openai_api_key"])

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0
        )

        antwort = response.choices[0].message.content

        rezept_daten = json.loads(antwort)
        return rezept_daten

    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Fehler beim Parsen der LLM-Antwort: {e}")
    except Exception as e:
        raise RuntimeError(f"❌ Fehler beim Abrufen der LLM-Antwort: {e}")

def rezept_speichern(db: Session, rezept_daten: dict):
    """Speichert ein extrahiertes Rezept und seine Zutaten in der DB."""
    rezept = Rezept(
        name=rezept_daten.get("name", "Unbenanntes Rezept"),
        beschreibung=rezept_daten.get("beschreibung", "")
    )
    db.add(rezept)
    db.commit()

    for z in rezept_daten.get("zutaten", []):
        zutat_name = z.get("name")
        menge = z.get("menge", 1)

        if not zutat_name:
            continue  # Fehlerhafte Zutat überspringen

        zutat_obj = db.query(Zutat).filter(Zutat.name.ilike(zutat_name)).first()

        if zutat_obj:
            rezept_zutat = RezeptZutat(
                rezept_id=rezept.id,
                zutat_id=zutat_obj.id,
                menge=menge
            )
            db.add(rezept_zutat)

    db.commit()
