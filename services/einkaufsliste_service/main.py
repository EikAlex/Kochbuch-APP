from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from shared.db_models.base import Base
from shared.db_models.einkaufsliste import Einkaufsliste
from shared.db_models.zutat import Zutat
from shared.db_models.vorrat import Vorrat
from database import engine, SessionLocal
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

# Schemas
class EinkaufInput(BaseModel):
    zutat_id: int
    menge: int

class EinkaufUpdateInput(BaseModel): # New model for updates
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
def update_menge(eintrag_id: int, update_data: EinkaufUpdateInput, db: Session = Depends(get_db)): # Use new model
    vorhanden = db.query(Einkaufsliste).filter(Einkaufsliste.id == eintrag_id).first()
    if not vorhanden:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    vorhanden.menge = update_data.menge # Use menge from the new model
    db.commit()
    return {"status": "ok"}

@app.post("/api/einkaufsliste/{eintrag_id}/kaufen")
def eintrag_kaufen(eintrag_id: int, db: Session = Depends(get_db)):
    eintrag = db.query(Einkaufsliste).options(joinedload(Einkaufsliste.zutat)).filter(Einkaufsliste.id == eintrag_id).first()
    if not eintrag:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")

    zutat = eintrag.zutat

    # Try to find an existing Vorrat entry for this zutat specifically with haltbar_bis IS NULL
    vorrat_eintrag_ohne_hbd = db.query(Vorrat).filter(
        Vorrat.zutat_id == zutat.id,
        Vorrat.haltbar_bis == None
    ).first()

    if vorrat_eintrag_ohne_hbd:
        vorrat_eintrag_ohne_hbd.menge += eintrag.menge
    else:
        # Create a new Vorrat entry with haltbar_bis=None
        neuer_vorrat_eintrag = Vorrat(
            zutat_id=zutat.id,
            menge=eintrag.menge,
            haltbar_bis=None 
            # mindestbestand is not handled here; could be a further enhancement
        )
        db.add(neuer_vorrat_eintrag)

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
