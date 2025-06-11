import streamlit as st
from db import SessionLocal, add_zutat_to_vorrat, delete_vorratseintrag, add_rezept, delete_zutat_from_db
import datetime
import llm_import
from openai import OpenAI
import requests
import easyocr
import numpy as np
from PIL import Image
from bs4 import BeautifulSoup
from models import Vorrat, Zutat, Rezept, Einkaufsliste
from util import check_haltbarkeit, defaul_einheit
from sqlalchemy.orm import joinedload

st.set_page_config(page_title="Koch mit mir!", layout="wide")

st.title("🥘 Digitale Kochbuch-App mit Vorratsverwaltung")
st.markdown(
    "Verwalte deine Rezepte und deinen Vorrat. Lass uns schauen, was du kochen kannst!")


# Tabs für die verschiedenen Funktionen
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📦 Vorrat", "📖 Rezepte", "🧠 Vorschläge", "🛒 Einkaufsliste", "📥 Rezept-Import"])

# TODO: Weitere Tabs/Optionen geplant
# [, "📅 Essensplaner", "⏱️ Timer / Kochmodus", 📷 OCR für Rezepte aus Fotos (z. B. mit Tesseract oder EasyOCR),🔄 LLM-Anbindung für selbst gehostete Modelle erstellen])

# 🔹 UI für Vorratspeicherung
with tab1:
    st.subheader("📥 Vorrat verwalten")

    # Auswahl zwischen Hinzufügen und Löschen
    action = st.radio("Wähle eine Aktion",
                      ("Zutat hinzufügen", "Zutat löschen"))

    db = SessionLocal()

    if action == "Zutat hinzufügen":
        with st.form("vorrat_form"):
            # Vorschlagsliste aus der Datenbank
            vorhandene_zutaten = db.query(Zutat.name).all()
            zutaten_liste = [z[0] for z in vorhandene_zutaten]

            # Vorschlag auswählen (optional)
            vorschlag = st.selectbox(
                "Vorschlag wählen (optional)",
                options=[""] + zutaten_liste,
                index=0,
                key="vorschlag"
            )

            # Eigene Eingabe – vorausgefüllt, wenn Vorschlag gewählt wurde
            name = st.text_input(
                "Zutat eingeben",
                value=st.session_state.get("vorschlag", ""),
                key="zutat_input"
            )

            # Einheit und Menge
            vorhandene_einheiten = db.query(Zutat.einheit).distinct().all()
            einheiten_liste = [e[0] for e in vorhandene_einheiten if e[0]] or [
                "Stück", "g", "ml"]
            einheit_von_zutat = None
            if vorschlag:
                zutat_obj = db.query(Zutat).filter(Zutat.name == vorschlag).first()
                if zutat_obj:
                    einheit_von_zutat = zutat_obj.einheit
            einheit = st.selectbox(
                        "Einheit",
                        options=einheiten_liste,
                        index=einheiten_liste.index(einheit_von_zutat) if einheit_von_zutat in einheiten_liste else 0,
                        key="einheit_input"
                    )
            menge = st.number_input(
                "Menge", min_value=1, step=1, key="menge_input")
            haltbar_bis = st.date_input(
                "Haltbar bis", value=datetime.date.today(), key="mhd_input")
            mindestbestand = st.number_input(
                "🧾 Optional: Mindestbestand", min_value=0, step=1, value=0, key="mb_input")

            submitted = st.form_submit_button("Hinzufügen")

        if submitted:
            # Prüfe, ob der gleiche Eintrag schon im Vorrat ist
            existiert_bereits = db.query(Vorrat).join(Zutat).filter(
                Zutat.name == name.strip().capitalize(),
                Vorrat.haltbar_bis == haltbar_bis
            ).first()

            if not existiert_bereits:
                try:
                    add_zutat_to_vorrat(
                        db,
                        name.strip().capitalize(),
                        einheit,
                        menge,
                        haltbar_bis,
                        mindestbestand if mindestbestand > 0 else None
                    )
                except Exception as e:
                    st.error(f"❌ Fehler beim Hinzufügen: {e}")
            else:
                try:
                    existiert_bereits.menge_vorhanden += menge
                    if mindestbestand > 0:
                        existiert_bereits.mindestbestand = mindestbestand
                    db.commit()
                except Exception as e:
                    st.error(f"❌ Fehler beim Aktualisieren des Vorrats: {e}")


    elif action == "Zutat löschen":
        # Zutat aus der Datenbank löschen falls man sich vertippt hat oder sie nicht mehr benötigt wird
        st.subheader("🗑️ Zutat aus der DatenBank löschen")

        # Zutat zum Löschen auswählen
        zutaten_liste = [z[0] for z in db.query(Zutat.name).all()]
        zutat_to_delete = st.selectbox(
            "Wähle eine Zutat zum Löschen", zutaten_liste)

        if zutat_to_delete:
            if st.button(f"❌ {zutat_to_delete} löschen"):
                try:
                    # Zutat-Objekt anhand des Namens holen
                    zutat_obj = db.query(Zutat).filter(
                        Zutat.name == zutat_to_delete).first()

                    if zutat_obj:
                        # Vorratseinträge zur Zutat löschen
                        eintraege = db.query(Vorrat).filter(
                            Vorrat.zutat_id == zutat_obj.id).all()
                        for eintrag in eintraege:
                            delete_vorratseintrag(db, eintrag.id)

                        # Danach die Zutat löschen
                        if delete_zutat_from_db(db, zutat_to_delete):
                            st.success(
                                f"✅ Zutat '{zutat_to_delete}' und zugehörige Vorräte wurden gelöscht!")
                        else:
                            st.error(
                                f"❌ Fehler: Zutat '{zutat_to_delete}' konnte nicht gelöscht werden.")
                    else:
                        st.warning(
                            f"⚠️ Zutat '{zutat_to_delete}' nicht gefunden.")

                except Exception as e:
                    st.error(f"❌ Fehler beim Löschen: {e}")
    db.close()

    st.divider()

    st.subheader("📦 Dein aktueller Vorrat")

    db = SessionLocal()
    try:
        eintraege = db.query(Vorrat).options(joinedload(Vorrat.zutat)).all()
        if eintraege:
            for eintrag in eintraege:
                col1, col2, col3, col4 = st.columns([3, 4, 2, 1])

                col1.write(f"**{eintrag.zutat.name}**")

                menge = eintrag.menge_vorhanden
                einheit = eintrag.zutat.einheit
                menge_text = f"{menge} {einheit}"

                if eintrag.mindestbestand and menge < eintrag.mindestbestand:
                    menge_text += f" 🔴 (unter Mindestbestand: {eintrag.mindestbestand} {einheit})"

                col2.write(menge_text)

                col3.markdown(check_haltbarkeit(
                    eintrag.haltbar_bis), unsafe_allow_html=True)

                if col4.button("🗑️", key=f"delete_{eintrag.id}"):
                    delete_vorratseintrag(db, eintrag.id)
                    st.success(f"✅ {eintrag.zutat.name} wurde gelöscht!")
                    st.rerun()
        else:
            st.info("Noch nichts im Vorrat.")
    finally:
        db.close()

# 🔹 UI für Rezepte
with tab2:
    db = SessionLocal()
    st.subheader("📥 Neues Rezept hinzufügen")

    # Init session state
    if "rezept_phase" not in st.session_state:
        st.session_state.rezept_phase = "start"
    if "rezept_zutaten_liste" not in st.session_state:
        st.session_state.rezept_zutaten_liste = []

    # Schritt 1: Basisdaten
    if st.session_state.rezept_phase == "start":
        with st.form("rezept_start_form"):
            rezeptname = st.text_input("Rezeptname")
            beschreibung = st.text_area("Beschreibung")
            portionen = st.number_input(
                "Anzahl Portionen", min_value=1, value=1, step=1)
            weiter = st.form_submit_button("➡️ Zutaten wählen")

            if weiter and rezeptname and portionen:
                st.session_state.rezeptname = rezeptname
                st.session_state.beschreibung = beschreibung
                st.session_state.portionen = portionen
                st.session_state.rezept_phase = "zutaten"
                st.rerun()

    # Schritt 2: Zutaten nach und nach hinzufügen
    elif st.session_state.rezept_phase == "zutaten":
        st.markdown(
            f"**Rezept:** {st.session_state.rezeptname} für {st.session_state.portionen} Portion(en)")

        zutaten = db.query(Zutat).all()
        zutaten_ids = [z.id for z in zutaten]
        zutaten_namen = [f"{z.name} ({z.einheit})" for z in zutaten]

        with st.form("zutat_hinzufuegen_form"):
            zutat_id = st.selectbox("Zutat auswählen", zutaten_ids,
                                    format_func=lambda x: zutaten_namen[zutaten_ids.index(x)])
            menge = st.number_input(
                "Menge für **1 Portion**", min_value=0.0, step=0.1)
            hinzufuegen = st.form_submit_button("➕ Zutat hinzufügen")

            if hinzufuegen and menge > 0:
                st.session_state.rezept_zutaten_liste.append({
                    "zutat_id": zutat_id,
                    "menge_pro_portion": menge
                })
                st.rerun()

        # Liste anzeigen
        st.subheader("🧾 Zutatenliste")
        if st.session_state.rezept_zutaten_liste:
            for i, eintrag in enumerate(st.session_state.rezept_zutaten_liste):
                z = db.query(Zutat).get(eintrag["zutat_id"])
                gesamtmenge = eintrag["menge_pro_portion"] * \
                    st.session_state.portionen
                col1, col2, col3, col4 = st.columns([4, 2, 3, 1])
                col1.write(z.name)
                col2.write(
                    f"{eintrag['menge_pro_portion']} {z.einheit} pro Portion")
                col3.write(f"{gesamtmenge} {z.einheit} gesamt")
                if col4.button("❌", key=f"del_zutat_{i}"):
                    st.session_state.rezept_zutaten_liste.pop(i)
                    st.rerun()
        else:
            st.info("Noch keine Zutat hinzugefügt.")

# TODO: Einbinden eines webcrawlers für Rezepte, bzw evtl mit einer LLM Rezepte extrahiren aus Bildern(OCR) und Texten aus Kochbüchern.
    # Rezept speichern
    if st.session_state.rezept_zutaten_liste:
        if st.button("✅ Rezept speichern"):
            # Überprüfen, ob der Rezeptname bereits existiert
            existing_rezept = db.query(Rezept).filter(
                Rezept.name == st.session_state.rezeptname).first()
            if existing_rezept:
                st.error("❌ Ein Rezept mit diesem Namen existiert bereits!")
            else:
                # Rezept speichern, wenn der Name eindeutig ist
                zutaten_liste = [
                    (e["zutat_id"], e["menge_pro_portion"]
                     * st.session_state.portionen)
                    for e in st.session_state.rezept_zutaten_liste
                ]
                add_rezept(
                    db,
                    st.session_state.rezeptname,
                    st.session_state.beschreibung,
                    zutaten_liste
                )
                st.success("🎉 Rezept gespeichert!")

                # Reset
                st.session_state.rezept_phase = "start"
                st.session_state.rezept_zutaten_liste = []
                st.rerun()
    st.divider()

    # Schritt 3: Rezepte anzeigen
    st.subheader("📖 Deine Rezepte")

    rezepte = db.query(Rezept).all()
    for i, rezept in enumerate(rezepte):
        with st.expander(rezept.name):
            st.markdown(rezept.beschreibung or "_Keine Beschreibung_")

            # Portionenauswahl – Default: 1
            portionen_input = st.number_input(
                f"👨‍🍳 Wie viele Portionen möchtest du kochen?",
                min_value=1, value=1, step=1, key=f"portionen_{rezept.id}"
            )

            st.markdown("**Zutaten:**")
            for rz in rezept.rezept_zutaten:
                z = rz.zutat
                berechnete_menge = rz.menge * portionen_input
                st.write(f"- {berechnete_menge} {z.einheit} {z.name}")

            # Löschen-Button
            delete_button = st.button(
                f"🗑️ Löschen {rezept.name}", key=f"delete_{rezept.id}_{i}"
            )
            if delete_button:
                try:
                    db.delete(rezept)
                    db.commit()
                    st.success(
                        f"✅ Rezept '{rezept.name}' wurde erfolgreich gelöscht!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Fehler beim Löschen des Rezepts: {e}")

# 🔹 UI für Vorschläge
with tab3:
    db = SessionLocal()
    st.subheader("🧠 Rezeptvorschläge basierend auf deinem Vorrat")

    vorrat = db.query(Vorrat).all()
    vorrats_map = {}
    for v in vorrat:
        if v.zutat_id not in vorrats_map:
            vorrats_map[v.zutat_id] = 0
        vorrats_map[v.zutat_id] += v.menge_vorhanden

    rezepte = db.query(Rezept).all()
    for rezept in rezepte:
        portionen_moeglich = float("inf")
        fehlende_zutaten = []

        for rz in rezept.rezept_zutaten:
            benoetigte_menge = rz.menge
            vorhandene_menge = vorrats_map.get(rz.zutat_id, 0)

            if vorhandene_menge <= 0:
                portionen_moeglich = 0
                fehlende_zutaten.append(
                    (rz.zutat.name, benoetigte_menge, rz.zutat.einheit))
            else:
                moegliche_portionen = vorhandene_menge / benoetigte_menge
                portionen_moeglich = min(
                    portionen_moeglich, moegliche_portionen)

                if vorhandene_menge < benoetigte_menge:
                    fehlende_zutaten.append(
                        (rz.zutat.name, benoetigte_menge - vorhandene_menge, rz.zutat.einheit))

        with st.expander(rezept.name):
            if portionen_moeglich >= 1:
                st.success(
                    f"✅ Du kannst ca. {int(portionen_moeglich)} Portion(en) kochen")
            else:
                st.warning("⚠️ Du hast nicht genug Vorrat für eine Portion.")
                if fehlende_zutaten:
                    st.markdown("**Fehlende Zutaten:**")
                    for name, diff, einheit in fehlende_zutaten:
                        st.write(f"- {diff:.2f} {einheit} {name}")

            st.markdown("**Zutatenübersicht pro Portion:**")
            for rz in rezept.rezept_zutaten:
                benoetigte_menge = rz.menge
                vorhandene_menge = vorrats_map.get(rz.zutat_id, 0)
                st.write(f"- {benoetigte_menge} {rz.zutat.einheit} {rz.zutat.name}"
                         f" --  (🧺 Vorrat: {vorhandene_menge} {rz.zutat.einheit})")

# 🔹 UI für Einkaufsliste
with tab4:
    db = SessionLocal()
    st.subheader("🛒 Einkaufsliste erstellen und verwalten")

    # Automatisch ergänzen: alle Vorräte prüfen, wo menge < mindestbestand
    auto_ergänzt = 0
    vorrat = db.query(Vorrat).options(joinedload(Vorrat.zutat)).all()
    for v in vorrat:
        if v.mindestbestand and v.menge_vorhanden < v.mindestbestand:
            differenz = v.mindestbestand - v.menge_vorhanden
            eintrag = db.query(Einkaufsliste).filter_by(
                zutat_id=v.zutat.id).first()
            if eintrag:
                eintrag.menge = max(eintrag.menge, differenz)
            else:
                db.add(Einkaufsliste(zutat_id=v.zutat.id, menge=differenz))
            auto_ergänzt += 1
    if auto_ergänzt > 0:
        db.commit()
        st.info(
            f"🧠 {auto_ergänzt} Zutaten wurden automatisch ergänzt (Mindestbestand unterschritten).")

    st.markdown("---")

    # Manuelles Hinzufügen zur Liste
    with st.expander("➕ Zutat zur Einkaufsliste hinzufügen"):
        zutaten = db.query(Zutat).all()
        name_to_id = {z.name: z.id for z in zutaten}
        auswahl = st.selectbox("Zutat auswählen", list(
            name_to_id.keys()), key="zutat_einkauf")
        menge = st.number_input("Menge", min_value=1.0,
                                step=1.0, key="menge_einkauf")
        if st.button("🛒 Zur Einkaufsliste hinzufügen", key="hinzufuegen_einkauf"):
            z_id = name_to_id[auswahl]
            bestehend = db.query(Einkaufsliste).filter_by(
                zutat_id=z_id).first()
            if bestehend:
                bestehend.menge += menge
            else:
                db.add(Einkaufsliste(zutat_id=z_id, menge=menge))
            db.commit()
            st.success("Hinzugefügt!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Aktuelle Einkaufsliste")

    einkaufsliste = db.query(Einkaufsliste).options(
        joinedload(Einkaufsliste.zutat)).all()

    if einkaufsliste:
        for eintrag in einkaufsliste:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            zutat = eintrag.zutat
            einheit = zutat.einheit or ""

            col1.write(f"**{zutat.name}**")

            key_input = f"menge_input_{eintrag.id}"

            neue_menge = col2.number_input(
                "",
                min_value=0,
                step=1,
                value=int(eintrag.menge),  # Initialer Standardwert
                key=key_input,             # Verknüpfung mit Session State
                label_visibility="collapsed"
            )

            if col3.button("💾", key=f"save_{eintrag.id}"):
                # Verwenden Sie den aktuellen Wert des Widgets aus diesem Durchlauf
                eintrag.menge = neue_menge
                db.commit()
                st.success(f"Menge von '{zutat.name}' aktualisiert!")
                st.rerun()

            #TODO: button noch bearbeiten mit funktion
            if col4.button("🛍️", key=f"bought_{eintrag.id}"):
                db.delete(eintrag)
                db.commit()
                st.success(f"'{zutat.name}' als gekauft markiert.")
                st.rerun()

            if col5.button("❌", key=f"remove_{eintrag.id}"):
                db.delete(eintrag)
                db.commit()
                st.success(f"'{zutat.name}' wurde entfernt.")
                st.rerun()
    else:
        st.info("🧺 Deine Einkaufsliste ist aktuell leer.")

    db.close()

with tab5:
    st.subheader("📥 Rezept-Import")

    option = st.radio(
        "Was möchtest du importieren?",
        ("📷 Bild hochladen", "🌐 Webseite angeben")
    )

    extrahierter_text = ""

    if option == "📷 Bild hochladen":
        bild = st.file_uploader("Lade ein Bild hoch", type=["jpg", "jpeg", "png"])
        if bild:
            st.image(bild, caption="Hochgeladenes Bild", use_column_width=True)

            img = Image.open(bild)
            img_array = np.array(img)

            reader = easyocr.Reader(["de", "en"], gpu=False)
            with st.spinner("🔍 Texterkennung läuft..."):
                result = reader.readtext(img_array, detail=0, paragraph=True)

            extrahierter_text = "\n".join(result)
            st.text_area("📄 Erkannter Text:", extrahierter_text, height=300)

    elif option == "🌐 Webseite angeben":
        url = st.text_input("Gib die URL einer Rezept-Webseite ein")
        if url:
            try:
                st.info(f"🔗 Webseite wird geladen: {url}")
                page = requests.get(url, timeout=10)
                soup = BeautifulSoup(page.content, "html.parser")
                texte = [p.get_text(strip=True) for p in soup.find_all(["p", "li"])]
                extrahierter_text = "\n".join(texte)
                st.text_area("📄 Gefundener Text:", extrahierter_text, height=300)
            except Exception as e:
                st.error(f"❌ Fehler beim Laden der Seite: {e}")

    if extrahierter_text:
        if st.button("🤖 Rezept aus Text extrahieren"):
            with st.spinner("🧠 LLM wird kontaktiert..."):
                try:
                    rezept_daten = llm_import.rezept_aus_text_extrahieren(extrahierter_text)

                    st.success("🎉 Text erfolgreich extrahiert!")

                    st.markdown("---")
                    with st.expander("🧾 Importiertes Rezept ansehen", expanded=True):
                        st.subheader(rezept_daten["name"])

                        st.markdown("### 📝 Beschreibung")
                        st.write(rezept_daten["beschreibung"])

                        st.markdown("### 🛒 Zutatenliste")
                        for z in rezept_daten["zutaten"]:
                            st.write(f"- {z['menge']} x {z['name']}")

                    st.markdown("---")
                    st.subheader("✏️ Nachbearbeiten (optional)")

                    rezeptname = st.text_input("Rezeptname", value=rezept_daten["name"], key="rezeptname_input")
                    beschreibung = st.text_area("Beschreibung", value=rezept_daten["beschreibung"], key="beschreibung_input")

                    edited_zutaten = []
                    st.markdown("### 🛒 Zutaten bearbeiten")
                    for i, z in enumerate(rezept_daten["zutaten"]):
                        col1, col2 = st.columns([3, 1])
                        key_suffix = f"{i}"
                        name = col1.text_input(f"Zutat {i+1} Name", value=z["name"], key=f"edit_name_{key_suffix}")
                        menge = col2.number_input(f"Menge {i+1}", value=z["menge"], min_value=0.0, step=1.0, key=f"edit_menge_{key_suffix}")
                        edited_zutaten.append({"name": name, "menge": menge})

                    if st.button("✅ Bearbeitete Version speichern"):
                        db = SessionLocal()
                        try:
                            neues_rezept = {
                                "name": rezeptname,
                                "beschreibung": beschreibung,
                                "zutaten": edited_zutaten
                            }

                            llm_import.rezept_speichern(db, neues_rezept)
                            st.success(f"🎉 Rezept '{rezeptname}' erfolgreich gespeichert!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Fehler beim Speichern: {e}")
                        finally:
                            db.close()

                    st.markdown("---")
                    if st.button("📖 Importiertes Rezept in Übersicht anzeigen"):
                        st.session_state.rezept_phase = "start"
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Fehler beim LLM-Import: {e}")


# 🔹 UI für Timer / Kochmodus
# with tab4:
#     db = SessionLocal()
#     st.subheader("⏱️ Kochen wir gemeinsam!")

# 🔹 UI für Essensplaner
# with tab4:
#     db = SessionLocal()
#     st.subheader("📅 Plane deine Woche")
