from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from shared.db_models.base import Base
from shared.db_models.rezept import Rezept
from shared.db_models.rezept_zutat import RezeptZutat
from shared.db_models.zutat import Zutat
from shared.database import SessionLocal, Base
from pydantic import BaseModel
from typing import List

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schema


class RezeptZutatInput(BaseModel):
    zutat_id: int
    menge: float


class RezeptInput(BaseModel):
    name: str
    beschreibung: str = ""
    zutaten: List[RezeptZutatInput]


@app.get("/api/rezepte")
def list_rezepte(db: Session = Depends(get_db)):
    rezepte = db.query(Rezept).all()
    result = []
    for rezept in rezepte:
        result.append({
            "id": rezept.id,
            "name": rezept.name,
            "beschreibung": rezept.beschreibung,
            "zutaten": [
                {
                    "zutat_id": rz.zutat_id,
                    "zutat_name": rz.zutat.name,
                    "menge": rz.menge,
                    "einheit": rz.zutat.einheit
                } for rz in rezept.rezept_zutaten
            ]
        })
    return result


@app.post("/api/rezepte")
def add_rezept(rezept_input: RezeptInput, db: Session = Depends(get_db)):
    existing = db.query(Rezept).filter(
        Rezept.name == rezept_input.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Rezeptname existiert bereits")

    rezept = Rezept(name=rezept_input.name,
                    beschreibung=rezept_input.beschreibung)
    db.add(rezept)
    db.commit()
    db.refresh(rezept)

    for z in rezept_input.zutaten:
        rz = RezeptZutat(
            rezept_id=rezept.id,
            zutat_id=z.zutat_id,
            menge=z.menge
        )
        db.add(rz)
    db.commit()
    return {"status": "ok", "id": rezept.id}


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
