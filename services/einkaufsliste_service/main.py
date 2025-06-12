from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from shared.db_models.base import Base
from shared.db_models.einkaufsliste import Einkaufsliste
from shared.db_models.vorrat import Vorrat
from shared.db_models.zutat import Zutat
from shared.database import engine, SessionLocal  # Zugriff auf shared/database
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

@app.get("/api/einkaufsliste", response_model=List[EinkaufResponse])
def get_einkaufsliste(db: Session = Depends(get_db)):
    eintraege = db.query(Einkaufsliste).options(joinedload(Einkaufsliste.zutat)).all()
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
    vorhanden = db.query(Einkaufsliste).filter(Einkaufsliste.id == eintrag_id).first()
    if not vorhanden:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    vorhanden.menge = eintrag.menge
    db.commit()
    return {"status": "ok"}

@app.post("/api/einkaufsliste/{eintrag_id}/kaufen")
def eintrag_kaufen(eintrag_id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Einkaufsliste).filter(Einkaufsliste.id == eintrag_id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")

    zutat = eintrag.zutat
    vorrat = db.query(Vorrat).filter(
        Vorrat.zutat_id == zutat.id
    ).first()

    if vorrat:
        vorrat.menge += eintrag.menge
    else:
        neuer = Vorrat(zutat_id=zutat.id, menge=eintrag.menge, haltbar_bis=None)
        db.add(neuer)

    db.delete(eintrag)
    db.commit()
    return {"status": "ok", "message": f"'{zutat.name}' in Vorrat übertragen"}

@app.delete("/api/einkaufsliste/{eintrag_id}")
def delete_eintrag(eintrag_id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Einkaufsliste).filter(Einkaufsliste.id == eintrag_id).first()
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
            eintrag = db.query(Einkaufsliste).filter_by(zutat_id=v.zutat.id).first()
            if eintrag:
                eintrag.menge = max(eintrag.menge, differenz)
            else:
                db.add(Einkaufsliste(zutat_id=v.zutat.id, menge=differenz))
            auto_erganzt += 1

    if auto_erganzt > 0:
        db.commit()

    return {"status": "ok", "hinzugefuegt": auto_erganzt}
