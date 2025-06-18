from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from shared.db_models import Base, Zutat, Rezept, RezeptZutat
from shared.database import engine, SessionLocal, get_db  # Zugriff auf shared/database
from pydantic import BaseModel
from typing import List

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Pydantic Schema


class RezeptZutatInput(BaseModel):
    zutat_id: int
    menge: float


class RezeptInput(BaseModel):
    name: str
    beschreibung: str = ""
    zutaten: List[RezeptZutatInput]


@app.get("/api/rezepte")
def get_rezepte(name: str = None, db: Session = Depends(get_db)):
    """
    Retrieves recipes. If a name is provided, retrieves the recipe by name.
    """
    if name:
        rezept = db.query(Rezept).filter_by(name=name).first()
        if not rezept:
            raise HTTPException(status_code=404, detail="Recipe not found.")
        return {
            "id": rezept.id,
            "name": rezept.name,
            "anleitung": rezept.anleitung,
            "portionen": rezept.portionen,
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
                "anleitung": rezept.anleitung,
                "portionen": rezept.portionen,
            }
            for rezept in rezepte
        ]


@app.post("/api/rezepte")
def create_rezept(rezept_data: RezeptInput, db: Session = Depends(get_db)):
    """
    Creates a new recipe and its associated ingredients.
    """
    # Check if the recipe already exists
    exists = db.query(Rezept).filter_by(name=rezept_data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Recipe already exists.")

    # Create the recipe
    rezept = Rezept(
        name=rezept_data.name,
        anleitung=rezept_data.beschreibung,
        portionen=rezept_data.portionen,
    )
    db.add(rezept)
    db.commit()  # Commit to get the recipe ID

    # Add ingredients to the recipe
    for zutat_data in rezept_data.zutaten:
        zutat = db.query(Zutat).get(zutat_data.zutat_id)
        if not zutat:
            raise HTTPException(
                status_code=404, detail=f"Ingredient with ID '{zutat_data.zutat_id}' not found."
            )
        rezept_zutat = RezeptZutat(
            rezept_id=rezept.id,
            zutat_id=zutat.id,
            menge=zutat_data.menge,
        )
        db.add(rezept_zutat)

    db.commit()
    return {"message": f"Recipe '{rezept_data.name}' created successfully."}


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
