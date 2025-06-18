from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.db_models import Base, Vorrat, Zutat
# Zugriff auf shared/database
from shared.database import engine, SessionLocal, get_db
from pydantic import BaseModel
import datetime
from typing import List, Optional

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Pydantic Schemas


class VorratInput(BaseModel):
    name: str
    menge: int
    einheit: str
    haltbar_bis: str
    mindestbestand: int = 0


class VorratUpdate(BaseModel):
    menge: int
    mindestbestand: int = 0


class VorratResponse(BaseModel):
    id: int
    name: str  # This will come from Zutat
    einheit: str  # This will come from Zutat
    menge: int
    haltbar_bis: Optional[datetime.date]
    mindestbestand: Optional[int]

    # No orm_mode needed if manually constructing


@app.get("/api/vorrat", response_model=List[VorratResponse])
def list_vorrat(db: Session = Depends(get_db)):
    # Ensure join is explicit if needed
    vorrat_items = db.query(Vorrat).join(Vorrat.zutat).all()

    response_list = []
    for v_item in vorrat_items:
        response_list.append(
            VorratResponse(
                id=v_item.id,
                name=v_item.zutat.name,
                einheit=v_item.zutat.einheit,
                menge=v_item.menge,
                haltbar_bis=v_item.haltbar_bis,
                mindestbestand=v_item.mindestbestand
            )
        )
    return response_list


@app.post("/api/vorrat")
def add_zutat_eintrag(vorrat: VorratInput, db: Session = Depends(get_db)):
    zutat = db.query(Zutat).filter(Zutat.name == vorrat.name).first()
    if not zutat:
        zutat = Zutat(name=vorrat.name, einheit=vorrat.einheit)
        db.add(zutat)
        db.commit()
        db.refresh(zutat)

    vorhandener_eintrag = db.query(Vorrat).filter(
        Vorrat.zutat_id == zutat.id,
        Vorrat.haltbar_bis == datetime.date.fromisoformat(vorrat.haltbar_bis)
    ).first()

    if vorhandener_eintrag:
        vorhandener_eintrag.menge += vorrat.menge
        vorhandener_eintrag.mindestbestand = vorrat.mindestbestand or vorhandener_eintrag.mindestbestand
        db.commit()
        return {"status": "updated", "id": vorhandener_eintrag.id}

    neues = Vorrat(
        zutat_id=zutat.id,
        menge=vorrat.menge,
        haltbar_bis=datetime.date.fromisoformat(vorrat.haltbar_bis),
        mindestbestand=vorrat.mindestbestand
    )
    db.add(neues)
    db.commit()
    return {"status": "ok", "id": neues.id}


@app.put("/api/vorrat/{vorrat_id}")
def update_vorrat(vorrat_id: int, update: VorratUpdate, db: Session = Depends(get_db)):
    eintrag = db.query(Vorrat).get(vorrat_id)
    if not eintrag:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")

    eintrag.menge = update.menge
    eintrag.mindestbestand = update.mindestbestand
    db.commit()
    return {"status": "ok", "id": eintrag.id, "menge": eintrag.menge}


@app.delete("/api/vorrat/{vorrat_id}")
def delete_vorrat(vorrat_id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Vorrat).get(vorrat_id)
    if not eintrag:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    db.delete(eintrag)
    db.commit()
    return {"status": "ok", "message": f"Eintrag {vorrat_id} gelöscht"}


@app.get("/api/zutaten/namen")
def get_zutaten_namen(db: Session = Depends(get_db)):
    zutaten = db.query(Zutat).order_by(Zutat.name).all()
    return [z.name for z in zutaten]


@app.get("/api/zutaten/einheiten")
def get_einheiten(db: Session = Depends(get_db)):
    einheiten = db.query(Zutat.einheit).distinct().all()
    return [e[0] for e in einheiten if e[0]]


@app.delete("/api/zutaten/{name}")
def delete_zutat(name: str, db: Session = Depends(get_db)):
    zutat = db.query(Zutat).filter(Zutat.name == name).first()
    if not zutat:
        raise HTTPException(status_code=404, detail="Zutat nicht gefunden")

    db.query(Vorrat).filter(Vorrat.zutat_id == zutat.id).delete()
    db.delete(zutat)
    db.commit()
    return {"status": "ok", "message": f"Zutat {name} gelöscht"}


@app.get("/api/zutaten")
def get_zutaten(db: Session = Depends(get_db)):
    zutaten = db.query(Zutat).order_by(Zutat.name).all()
    return [{"id": z.id, "name": z.name, "einheit": z.einheit} for z in zutaten]
