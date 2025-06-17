from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from shared.database import get_db, engine  # Zugriff auf shared/database
from shared.db_models import Base, Zutat, Rezept, RezeptZutat
from llm_core import extrahiere_rezept_daten
from pydantic import BaseModel

Base.metadata.create_all(bind=engine)

app = FastAPI()

class ExtraktionRequest(BaseModel):
    text: str

@app.post("/api/extrahieren")
def extrahiere(text_input: ExtraktionRequest, db: Session = Depends(get_db)):
    try:
        rezept_daten = extrahiere_rezept_daten(text_input.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der LLM-Antwort: {e}")

    rezept = Rezept(
        name=rezept_daten["name"],
        beschreibung=rezept_daten["beschreibung"]
    )
    db.add(rezept)
    db.commit()
    db.refresh(rezept)

    for z in rezept_daten["zutaten"]:
        zutat = db.query(Zutat).filter(Zutat.name.ilike(z["name"])).first()
        if not zutat:
            continue
        db.add(RezeptZutat(
            rezept_id=rezept.id,
            zutat_id=zutat.id,
            menge=z["menge"]
        ))

    db.commit()
    return {"status": "ok", "rezept_id": rezept.id}
