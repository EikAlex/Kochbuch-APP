from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, joinedload
from shared.db_models.base import Base
from shared.db_models.rezept import Rezept
from shared.db_models.vorrat import Vorrat
from shared.db_models.zutat import Zutat
from shared.db_models.rezept_zutat import RezeptZutat
# Zugriff auf shared/database
from shared.database import engine, SessionLocal, get_db

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/api/vorschlaege")
def get_vorschlaege(db: Session = Depends(get_db)):
    rezepte = db.query(Rezept).options(joinedload(
        Rezept.rezept_zutaten).joinedload(RezeptZutat.zutat)).all()
    vorrat = db.query(Vorrat).options(joinedload(Vorrat.zutat)).all()

    # Map: zutat_id -> gesamte vorhandene Menge
    vorrats_map = {}
    for v in vorrat:
        if v.zutat_id not in vorrats_map:
            vorrats_map[v.zutat_id] = 0
        vorrats_map[v.zutat_id] += v.menge

    vorschlaege = []

    for rezept in rezepte:
        portionen_moeglich = float("inf")
        fehlende = []
        zutaten_details = []

        for rz in rezept.rezept_zutaten:
            benoetigte_menge = rz.menge
            vorhandene_menge = vorrats_map.get(rz.zutat_id, 0)

            zutaten_details.append({
                "name": rz.zutat.name,
                "menge": benoetigte_menge,
                "einheit": rz.zutat.einheit,
                "vorrat": vorhandene_menge
            })

            if vorhandene_menge <= 0:
                portionen_moeglich = 0
                fehlende.append({
                    "name": rz.zutat.name,
                    "fehlt": benoetigte_menge,
                    "einheit": rz.zutat.einheit
                })
            else:
                moegliche_portionen = vorhandene_menge / benoetigte_menge
                portionen_moeglich = min(
                    portionen_moeglich, moegliche_portionen)

                if vorhandene_menge < benoetigte_menge:
                    fehlende.append({
                        "name": rz.zutat.name,
                        "fehlt": benoetigte_menge - vorhandene_menge,
                        "einheit": rz.zutat.einheit
                    })

        vorschlaege.append({
            "rezept": rezept.name,
            "portionen_moeglich": int(portionen_moeglich),
            "fehlende": fehlende,
            "zutaten": zutaten_details
        })

    return vorschlaege
