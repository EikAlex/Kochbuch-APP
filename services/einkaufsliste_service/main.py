from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from shared.db_models import Base, Vorrat, Zutat, Einkaufsliste, Rezept, RezeptZutat
# Zugriff auf shared/database
from shared.database import engine, SessionLocal, get_db
from pydantic import BaseModel
from typing import List
import datetime

app = FastAPI()


class EinkaufInput(BaseModel):
    zutat_id: int
    menge: int


class EinkaufUpdateInput(BaseModel):
    menge: int


class EinkaufResponse(BaseModel):
    id: int
    zutat: str
    menge: int
    einheit: str


class VorratInput(BaseModel):
    name: str
    menge: int
    einheit: str
    haltbar_bis: str
    mindestbestand: int = None


class RezeptZutatInput(BaseModel):
    zutat_id: int
    menge: int


class RezeptInput(BaseModel):
    name: str
    beschreibung: str
    zutaten: List[RezeptZutatInput]


@app.get("/api/einkaufsliste", response_model=List[EinkaufResponse])
def get_einkaufsliste(db: Session = Depends(get_db)):
    eintraege = db.query(Einkaufsliste).options(
        joinedload(Einkaufsliste.zutat)).all()
    return [
        EinkaufResponse(
            id=e.id,
            zutat=e.zutat.name,
            menge=e.menge,
            einheit=e.zutat.einheit or ""
        ) for e in eintraege
    ]


@app.post("/api/einkaufsliste")
def add_zutat(eintrag: EinkaufInput, db: Session = Depends(get_db)):
    neuer = Einkaufsliste(zutat_id=eintrag.zutat_id, menge=eintrag.menge)
    db.add(neuer)
    db.commit()
    db.refresh(neuer)
    return {"status": "ok", "id": neuer.id}


@app.put("/api/einkaufsliste/{eintrag_id}")
def update_menge(eintrag_id: int, eintrag: EinkaufUpdateInput, db: Session = Depends(get_db)):
    vorhanden = db.query(Einkaufsliste).filter(
        Einkaufsliste.id == eintrag_id).first()
    if not vorhanden:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    vorhanden.menge = eintrag.menge
    db.commit()
    return {"status": "ok"}


@app.post("/api/einkaufsliste/{eintrag_id}/kaufen")
def eintrag_kaufen(eintrag_id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Einkaufsliste).filter(
        Einkaufsliste.id == eintrag_id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")

    zutat = eintrag.zutat
    vorrat = db.query(Vorrat).filter(
        Vorrat.zutat_id == zutat.id
    ).first()

    if vorrat:
        vorrat.menge += eintrag.menge
    else:
        neuer = Vorrat(zutat_id=zutat.id,
                       menge=eintrag.menge, haltbar_bis=None)
        db.add(neuer)

    db.delete(eintrag)
    db.commit()
    return {"status": "ok", "message": f"'{zutat.name}' in Vorrat übertragen"}


@app.delete("/api/einkaufsliste/{eintrag_id}")
def delete_eintrag(eintrag_id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Einkaufsliste).filter(
        Einkaufsliste.id == eintrag_id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    db.delete(eintrag)
    db.commit()
    return {"status": "ok", "message": "Eintrag gelöscht"}


@app.post("/api/einkaufsliste/auto")
def auto_auffuellen(db: Session = Depends(get_db)):
    auto_erganzt = 0

    vorrat = db.query(Vorrat).options(joinedload(Vorrat.zutat)).all()
    for v in vorrat:
        if v.mindestbestand and v.menge < v.mindestbestand:
            differenz = v.mindestbestand - v.menge
            eintrag = db.query(Einkaufsliste).filter_by(
                zutat_id=v.zutat.id).first()
            if eintrag:
                eintrag.menge = max(eintrag.menge, differenz)
            else:
                db.add(Einkaufsliste(zutat_id=v.zutat.id, menge=differenz))
            auto_erganzt += 1

    if auto_erganzt > 0:
        db.commit()

    return {"status": "ok", "hinzugefuegt": auto_erganzt}


@app.post("/api/vorrat")
def add_zutat_eintrag(vorrat: VorratInput, db: Session = Depends(get_db)):
    try:
        haltbar_bis_date = datetime.date.fromisoformat(vorrat.haltbar_bis)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Ungültiges Datum für 'haltbar_bis'")

    zutat = db.query(Zutat).filter(Zutat.name == vorrat.name).first()
    if not zutat:
        zutat = Zutat(name=vorrat.name, einheit=vorrat.einheit)
        db.add(zutat)
        db.commit()
        db.refresh(zutat)

    vorhandener_eintrag = db.query(Vorrat).filter(
        Vorrat.zutat_id == zutat.id,
        Vorrat.haltbar_bis == haltbar_bis_date
    ).first()

    if vorhandener_eintrag:
        vorhandener_eintrag.menge += vorrat.menge
        vorhandener_eintrag.mindestbestand = vorrat.mindestbestand or vorhandener_eintrag.mindestbestand
        db.commit()
        return {"status": "updated", "id": vorhandener_eintrag.id}

    neues = Vorrat(
        zutat_id=zutat.id,
        menge=vorrat.menge,
        haltbar_bis=haltbar_bis_date,
        mindestbestand=vorrat.mindestbestand
    )
    db.add(neues)
    db.commit()
    return {"status": "ok", "id": neues.id}


@app.post("/api/rezepte")
def create_rezept(rezept_data: RezeptInput, db: Session = Depends(get_db)):
    if not rezept_data.zutaten:
        raise HTTPException(status_code=400, detail="Keine Zutaten angegeben")

    exists = db.query(Rezept).filter_by(name=rezept_data.name).first()
    if exists:
        raise HTTPException(
            status_code=400, detail="Rezept existiert bereits.")

    rezept = Rezept(
        name=rezept_data.name,
        beschreibung=rezept_data.beschreibung,
    )
    db.add(rezept)
    db.commit()

    for zutat_data in rezept_data.zutaten:
        zutat = db.query(Zutat).get(zutat_data.zutat_id)
        if not zutat:
            raise HTTPException(
                status_code=404, detail=f"Zutat mit ID '{zutat_data.zutat_id}' nicht gefunden."
            )
        rezept_zutat = RezeptZutat(
            rezept_id=rezept.id,
            zutat_id=zutat.id,
            menge=zutat_data.menge,
        )
        db.add(rezept_zutat)

    db.commit()
    return {"status": "ok", "message": f"Rezept '{rezept_data.name}' erfolgreich erstellt."}
