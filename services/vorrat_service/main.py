from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.db_models.base import Base
from shared.db_models.zutat import Zutat
from shared.db_models.vorrat import Vorrat
from database import engine, SessionLocal
from pydantic import BaseModel
import datetime

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.get("/api/vorrat")
def list_vorrat(db: Session = Depends(get_db)):
    vorrat = db.query(Vorrat).join(Zutat).all()
    return [{
        "id": v.id,
        "name": v.zutat.name,
        "einheit": v.zutat.einheit,
        "menge": v.menge,
        "haltbar_bis": v.haltbar_bis.isoformat() if v.haltbar_bis else None,
        "mindestbestand": v.mindestbestand
    } for v in vorrat]

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