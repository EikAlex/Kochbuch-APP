# 🥘 Digitale Kochbuch-App mit integrierter Vorratsverwaltung und REST-API Services

Willkommen bei deiner digitalen Kochbuch-App!  
Diese Anwendung basiert jetzt auf einer **vollständig REST-API-basierten Microservice-Architektur**, realisiert mit **FastAPI** und **Pydantic**. Jeder Tab der App läuft als eigenständiger Microservice in einem separaten Docker-Container, was die Wartbarkeit erheblich verbessert und die Fehlertoleranz steigert.

Du profitierst dadurch von modularer Funktionalität, besserer Skalierbarkeit und einer klaren Trennung der Komponenten.

Die App bietet weiterhin eine moderne und intuitive Benutzeroberfläche zur Verwaltung von Rezepten und Vorräten.

- Entwickelt mit **Python** und **Streamlit**
- Speicherung aller Daten in einer **PostgreSQL-Datenbank**
- Verwaltung der Datenbank mit **SQLAlchemy** und **Docker**
- Integration eines **ChatGPT-gestützten Import-Systems**: Rezepte können bequem aus Bildern oder Webseiten automatisch extrahiert werden  
- **Modularer Microservice-Ansatz:** Jeder Tab kommuniziert über REST-APIs, umgesetzt mit **FastAPI** und **Pydantic**, ausgeführt in isolierten Docker-Containern

---

## 🚀 Features

- 🧺 **Vorratsverwaltung:** Behalte den Überblick über Zutaten, Bestände und Haltbarkeitsdaten
- 📖 **Rezeptverwaltung:** Hinzufügen, Bearbeiten und Anzeigen von Rezepten
- 🔄 **Integration:** Verknüpfung von Rezepten mit aktuellen Vorratsdaten
- 🧠 **Intelligenter Import:** OCR- und LLM-gestütztes Erfassen neuer Rezepte
- 🛒 **Einkaufslisten-Generator:** Automatische Erstellung basierend auf Vorräten und Rezeptbedarf
- 🐳 **Containerisiert:** Vollständige Bereitstellung via Docker für einfaches Setup

---

## 🛠️ Tech-Stack

| Komponente       | Beschreibung                         |
|------------------|--------------------------------------|
| 🐍 Python         | Programmiersprache der Wahl          |
| 🌐 Streamlit      | Web-Interface für die Anwendung      |
| ⚡ FastAPI         | Framework für Microservice-APIs      |
| 📦 Pydantic       | Datenvalidierung und -modellierung   |
| 🐘 PostgreSQL     | Datenbank für Rezepte & Vorräte      |
| 🧪 SQLAlchemy     | ORM für effiziente Datenbankzugriffe |
| 🐳 Docker         | Containerisierung & Setup-Management |

---

## 📚 Ziel

Verwalte deine Küche einfach, modern und effizient – entdecke, plane und organisiere deine Rezepte und Vorräte an einem Ort!

---

## 🧱 Projektstruktur (grober Überblick)

```bash
Kochbuch-App/
├── frontend/                   ← Streamlit UI
│   ├── app.py                  ← Hauptseite mit Tabs
│   ├── requiremnts.txt         ← requirments für das Frontend
│   ├── Dockerfile
│   └── tabs/
│       ├── vorrat_tab.py       ← REST-basierter Tab (spricht Service)
│       ├── rezepte_tab.py
│       ├── vorschlag_tab.py
│       ├── einkaufsliste_tab.py
│       └── import_tab.py
│ 
│
├── services/                   ← Jeder Dienst ist ein Microservice
│   ├── init_services/
│   │   ├── init_db.py          ← initialsierung der Grundzuteten und eines Testrezeptes
│   │   └── Dockerfile
│   ├── vorrat_service/
│   │   ├── main.py             ← FastAPI-Server für Vorrat
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── rezept_service/         ← sinngemäßer Aufbau wie vorrat_service
│   ├── vorschlag_service/
│   ├── einkaufsliste_service/
│   └── rezept-import_service/  
│
│
├── shared/                     ← geteilte SQLAlchemy-Modelle und Skrips
│   ├── db_models/
│   │   ├── base.py
│   │   ├── einkaufsliste.py
│   │   ├── rezept_zutat.py
│   │   ├── rezept.py
│   │   ├── vorrat.py
│   │   └── zutat.py
│   ├── scripts
│       └── wit-for-it.sh
│   ├── config.py                ← Konfiguration der Database 
│   ├── database.py              ← Initialisierung der Database 
│   └── utils.py                 ← Helper Funktionen 
│
├── docker-compose.yml         ← Zum Hochfahren aller Services + DB  
├── .env                       ← API-Keys, DB-URL, Secrets
├── templates.py               ← Templates für Icons
├── LICENSE
└── README.md
```

---
## 🐳 Deployment mit Docker: Microservice-Architektur & Netzwerk

Diese Anwendung verwendet eine **Microservice-Architektur**, bei der jede Komponente (Frontend und Backend-Services) in einem eigenen **Docker-Container** läuft. Alle Container sind über ein gemeinsames Docker-Netzwerk verbunden, was die interne Kommunikation stabil und sicher macht.

---

### 📦 Services als Container

Jede der folgenden Komponenten wird in einem separaten Container betrieben:

| Service                  | Beschreibung                                 |
|--------------------------|----------------------------------------------|
| `frontend`               | Streamlit-UI mit Tabs für die Webanwendung   |
| `init_service`           | Datenbank-Service für Initialisierung von Grundzutaten und eines Testrezeptes, wird nach inplemtierung wieder beendet       |
| `vorrat_service`         | FastAPI-Service für Vorratsverwaltung        |
| `rezepte_service`        | FastAPI-Service für Rezepteverwaltung        |
| `vorschlag_service`      | FastAPI-Service für Rezeptvorschläge         |
| `einkaufsliste_service`  | FastAPI-Service für Einkaufsliste            |
| `import_service`         | FastAPI-Service zum Datenimport              |
| `postgres`               | PostgreSQL-Datenbank für alle Services       |

---

### 🔗 Gemeinsames Docker-Netzwerk

Alle Services sind über ein benutzerdefiniertes Docker-Netzwerk (z. B. `app_net`) miteinander verbunden:

- Ermöglicht **sichere Kommunikation** zwischen Containern
- **DNS-basiertes Service-Discovery** (`http://rezepte_service:8000`)
- Kein externer Zugriff nötig – alles bleibt **intern und isoliert**


## ✅ Vorteile der Docker-basierten Microservice-Architektur

Die gewählte Architektur bringt zahlreiche Vorteile für Entwicklung, Deployment und Betrieb:

### 🔄 Skalierbarkeit
- Jeder Microservice kann **unabhängig skaliert** werden – horizontal (mehr Instanzen) oder vertikal (mehr Ressourcen).
- Ermöglicht eine **bedarfsorientierte Ressourcenverteilung** bei hoher Last (z. B. mehr Vorschlagsdienste bei komplexer Logik).

### 🌍 Verteilbarkeit
- Jeder Service kann theoretisch auf einem **eigenen Server** oder **in der Cloud** betrieben werden.
- Bereit für **Docker Swarm**, **Kubernetes** oder andere Orchestrierungsplattformen.
- Erleichtert den **globalen Betrieb** durch georedundante Verteilung.

### 🔗 Isolation & Unabhängigkeit
- Services sind voneinander isoliert – Fehler in einem Service wirken sich nicht direkt auf andere aus.
- Unabhängiges **Entwickeln, Testen, Deployen** möglich.

### 🧩 Modularität & Wartbarkeit
- Die Anwendung ist in **logisch getrennte Komponenten** gegliedert.
- Neue Funktionen lassen sich als eigenständige Services integrieren.
- Änderungen in einem Bereich erfordern **keine Anpassungen an anderen** Services.

### 🧪 Einheitliche Umgebung
- Alle Services laufen in **identisch definierten Containern** – auf jedem System gleich.
- Verhindert „It works on my machine“-Probleme.
- Vereinfachtes Onboarding für neue Entwickler.

### 🔐 Sicherheit & Netzwerktrennung
- Kommunikation erfolgt nur über das **interne Docker-Netzwerk**.
- Kein unnötiger Zugriff von außen auf interne APIs.
- Dienste können gezielt nach außen freigegeben oder abgeschottet werden.

---

Diese Architektur ist eine robuste Grundlage für **wachstumsfähige**, **wartbare** und **zukunftssichere** Webanwendungen.

---

## 1. Klone das Repository
git clone https://github.com/EikAlex/Kochbuch-App.git

cd Cocking-App

## 2. Starte die Anwendung
docker-compose up --build (<Docker 20.10)

docker compose up --build

Falls die Datenbank langsamer startet als die Web-App und wait-for-it.sh nicht korrekt greift, kannst du mit Strg + C abbrechen und anschließend neu starten.
Dieses Vorgehen ist nur nötig, wenn wait-for-it.sh Verbindungsprobleme zur Datenbank verursacht.

## 3. Link zur Webapp
http://localhost:8501/

## 4. Neustart und leeren der Datenbank
docker compose down

docker volume rm kochbuch-app_pgdata

## 5. Nutzen der Rezept-Import
Um die Rezept-Import Funktion nutzen zu können muss in .env,
eine datei mit API-Key angelgt werden.

```bash
[openai]
openai_api_key = "sk -xxxxxxxxx"
```
---
## Diagramme 
---
### Architekturdiagramm/Komponentendiagramm
```mermaid
graph TD
    subgraph Frontend
        direction TB
        A1["app.py (Tabs)"]
        A2[vorrat_tab.py]
        A3[rezepte_tab.py]
        A4[vorschlag_tab.py]
        A5[einkaufsliste_tab.py]
        A6[import_tab.py]
    end

    subgraph Backend
        direction TB
        B1[vorrat_service]
        B2[rezepte_service]
        B3[vorschlag_service]
        B4[einkaufsliste_service]
        B5[import_service]
        B6[init_service]
    end

    subgraph Shared
        direction TB
        C1[PostgreSQL-Datenbank]
        C2["shared/db_models (SQLAlchemy)"]
    end

    %% Verbindungen Frontend zu Backend
    A2 -->|REST API| B1
    A3 -->|REST API| B2
    A4 -->|REST API| B3
    A5 -->|REST API| B4
    A6 -->|REST API| B5

    %% Backend zu DB & Shared Models
    B1 --> C1
    B2 --> C1
    B3 --> C1
    B4 --> C1
    B5 --> C1
    B6 --> C1

    B1 --> C2
    B2 --> C2
    B3 --> C2
    B4 --> C2
    B5 --> C2
    B6 --> C2

```
---
### Sequenz-Diagramm
```mermaid
sequenceDiagram
    participant User
    participant Frontend as Streamlit UI
    participant VorratService as Vorrat Service (FastAPI)
    participant RezepteService as Rezepte Service (FastAPI)
    participant VorschlagService as Vorschlag Service (FastAPI)
    participant EinkaufslisteService as Einkaufsliste Service (FastAPI)
    participant ImportService as Import Service (FastAPI)
    participant InitService as Init Service (FastAPI)
    participant DB as PostgreSQL + Shared Models

    User->>Frontend: Öffnet App / Wechselt Tab
    alt Vorrat Tab
        Frontend->>VorratService: REST API Anfrage
        VorratService->>DB: Daten abfragen/aktualisieren
        DB-->>VorratService: Daten zurück
        VorratService-->>Frontend: Antwort
    end

    alt Rezepte Tab
        Frontend->>RezepteService: REST API Anfrage
        RezepteService->>DB: Daten abfragen/aktualisieren
        DB-->>RezepteService: Daten zurück
        RezepteService-->>Frontend: Antwort
    end

    alt Vorschlag Tab
        Frontend->>VorschlagService: REST API Anfrage
        VorschlagService->>DB: Daten abfragen/aktualisieren
        DB-->>VorschlagService: Daten zurück
        VorschlagService-->>Frontend: Antwort
    end

    alt Einkaufsliste Tab
        Frontend->>EinkaufslisteService: REST API Anfrage
        EinkaufslisteService->>DB: Daten abfragen/aktualisieren
        DB-->>EinkaufslisteService: Daten zurück
        EinkaufslisteService-->>Frontend: Antwort
    end

    alt Import Tab
        Frontend->>ImportService: REST API Anfrage
        ImportService->>DB: Daten abfragen/aktualisieren
        DB-->>ImportService: Daten zurück
        ImportService-->>Frontend: Antwort
    end
```

---
### Klassen-Diagramm
```mermaid
classDiagram
    class Zutat {
        +int id
        +str name
        +str einheit
    }

    class Rezept {
        +int id
        +str name
        +str beschreibung
    }

    class RezeptZutat {
        +int rezept_id
        +int zutat_id
        +int menge
    }

    class Vorrat {
        +int id
        +int zutat_id
        +int menge
        +date haltbar_bis
        +int mindestbestand
    }

    class Einkaufsliste {
        +int id
        +int zutat_id
        +int menge
    }

    %% Beziehungen
    Rezept --> RezeptZutat : rezept_zutaten
    Zutat --> RezeptZutat : rezept_zutaten
    RezeptZutat --> Rezept : rezept
    RezeptZutat --> Zutat : zutat

    Zutat --> Vorrat : vorrat
    Zutat --> Einkaufsliste : einkaufsliste
```
---
###  Deployment-Diagramm (Docker-Architektur)

```mermaid
graph TD
    subgraph Client
        Browser[Benutzer-Browser]
    end

    subgraph DockerHost
        Streamlit[Frontend: Streamlit-App Container]

        Vorrat[Vorrat-Service Container]
        Rezepte[Rezepte-Service Container]
        Vorschlag[Vorschlag-Service Container]
        Einkaufsliste[Einkaufsliste-Service Container]
        Import[Import-Service Container]
        Init[Init-Service Container]

        Postgres[(PostgreSQL-Datenbank)]
    end

    Browser -->|HTTP| Streamlit

    Streamlit -->|REST| Vorrat
    Streamlit -->|REST| Rezepte
    Streamlit -->|REST| Vorschlag
    Streamlit -->|REST| Einkaufsliste
    Streamlit -->|REST| Import

    Vorrat --> Postgres
    Rezepte --> Postgres
    Vorschlag --> Postgres
    Einkaufsliste --> Postgres
    Import --> Postgres
    Init --> Postgres
```

---
## Erstellt von Alexander Schmal für die Abgabe des Mobile Applikationen Moduls 
