# Brawl Stars Battle Log API

Eine FastAPI-basierte REST-API zum Abrufen von Brawl Stars Battle Log Daten aus einer MySQL-Datenbank.

## Features

- Abrufen aller Battle Logs
- Filtern von Battle Logs nach Spieler-Tag
- Detaillierte Abfrage einzelner Battle Logs
- Automatische Swagger-Dokumentation unter `/docs`

## Technologie-Stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- MySQL
- Uvicorn

## Installation

1. Repository klonen:
git clone https://github.com/IHR_USERNAME/BS-Stats-API.git
cd BS-Stats-API

2. Virtuelle Umgebung erstellen und aktivieren:

python -m venv venv
.\venv\Scripts\activate #Windows
source venv/bin/activate #Linux/Mac

3. Abhängigkeiten installieren:
pip install -r requirements.txt

4. Umgebungsvariablen konfigurieren:
- Kopiere `.env.example` zu `.env`
- Trage deine Datenbank-Zugangsdaten in die `.env` ein


## Verwendung

1. Server starten:
uvicorn main:app --reload

2. API-Endpunkte:
- `GET /battle-data`: Alle Battle Logs abrufen
- `GET /battle-data/{player_tag}`: Battle Logs eines bestimmten Spielers abrufen
- `GET /battle-data/{player_tag}/{battle_time}/{brawler_id}`: Spezifischen Battle Log abrufen

3. API-Dokumentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
