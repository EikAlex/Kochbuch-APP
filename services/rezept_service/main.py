from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from shared.db_models import Base, Zutat, Rezept, RezeptZutat
# Zugriff auf shared/database
from shared.database import engine, SessionLocal, get_db
from pydantic import BaseModel
from typing import List

app = FastAPI()


class RezeptZutatInput(BaseModel):
    zutat_id: int
    menge: float


class RezeptInput(BaseModel):
    name: str
    beschreibung: str = ""
    zutaten: List[RezeptZutatInput]


@app.get("/api/rezepte")
def get_rezepte(name: str = None, db: Session = Depends(get_db)):
    if name:
        rezept = db.query(Rezept).filter_by(name=name).first()
        if not rezept:
            raise HTTPException(status_code=404, detail="Recipe not found.")
        return {
            "id": rezept.id,
            "name": rezept.name,
            "beschreibung": rezept.beschreibung,
            "zutaten": [
                {
                    "zutat_name": rz.zutat.name,
                    "menge": rz.menge,
                    "einheit": rz.zutat.einheit,
                }
                for rz in rezept.rezept_zutaten
            ],
        }
    else:
        rezepte = db.query(Rezept).all()
        return [
            {
                "id": rezept.id,
                "name": rezept.name,
                "beschreibung": rezept.beschreibung,
                "zutaten": [
                    {
                        "zutat_name": rz.zutat.name,
                        "menge": rz.menge,
                        "einheit": rz.zutat.einheit,
                    }
                    for rz in rezept.rezept_zutaten
                ],
            }
            for rezept in rezepte
        ]


@app.post("/api/rezepte")
def create_rezept(rezept_data: RezeptInput, db: Session = Depends(get_db)):
    try:
        # Validierung der Eingaben
        if not rezept_data.name or not rezept_data.beschreibung or not rezept_data.zutaten:
            raise HTTPException(status_code=400, detail="Ungültige Eingabe: Name, Beschreibung und Zutaten müssen angegeben werden.")

        # Prüfe, ob das Rezept bereits existiert
        exists = db.query(Rezept).filter_by(name=rezept_data.name).first()
        if exists:
            raise HTTPException(status_code=400, detail="Rezept existiert bereits.")

        # Rezept erstellen
        rezept = Rezept(
            name=rezept_data.name,
            beschreibung=rezept_data.beschreibung,  # Anpassung an das Modell
        )
        db.add(rezept)
        db.commit()

        # Zutaten hinzufügen
        for zutat_data in rezept_data.zutaten:
            zutat = db.query(Zutat).get(zutat_data.zutat_id)
            if not zutat:
                raise HTTPException(status_code=404, detail=f"Zutat mit ID '{zutat_data.zutat_id}' nicht gefunden.")
            rezept_zutat = RezeptZutat(
                rezept_id=rezept.id,
                zutat_id=zutat.id,
                menge=zutat_data.menge,
            )
            db.add(rezept_zutat)

        db.commit()
        return {"message": f"Rezept '{rezept_data.name}' erfolgreich erstellt."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen des Rezepts: {str(e)}")


@app.delete("/api/rezepte/{rezept_id}")
def delete_rezept(rezept_id: int, db: Session = Depends(get_db)):
    rezept = db.query(Rezept).get(rezept_id)
    if not rezept:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    db.query(RezeptZutat).filter(RezeptZutat.rezept_id == rezept.id).delete()
    db.delete(rezept)
    db.commit()
    return {"status": "ok", "message": f"Rezept {rezept.name} gelöscht"}


@app.get("/api/zutaten")
def get_zutaten(db: Session = Depends(get_db)):
    zutaten = db.query(Zutat).order_by(Zutat.name).all()
    return [{"id": z.id, "name": z.name, "einheit": z.einheit} for z in zutaten]
