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

## Datenbankstruktur

Die API erwartet eine MySQL-Datenbank mit einer Tabelle `battle_logs`, die folgende Struktur aufweist:

| Feldname              | Typ          | Null | Schlüssel | Beschreibung                    |
|----------------------|--------------|------|------------|--------------------------------|
| player_tag           | varchar(50)  | Nein | PK        | Eindeutige Spieler-ID          |
| battle_time          | datetime     | Nein | PK        | Zeitpunkt des Kampfes          |
| brawler_id           | int          | Nein | PK        | ID des verwendeten Brawlers    |
| brawler_name         | varchar(50)  | Ja   |           | Name des Brawlers              |
| brawler_power        | int          | Ja   |           | Power-Level des Brawlers       |
| brawler_trophies     | int          | Ja   |           | Trophäen des Brawlers         |
| brawler_trophy_change| int          | Ja   |           | Trophäenänderung des Brawlers |
| player_name          | varchar(50)  | Ja   |           | Name des Spielers              |
| event_id             | int          | Ja   |           | Event-ID                       |
| event_mode           | varchar(50)  | Ja   |           | Spielmodus                     |
| event_map            | varchar(100) | Ja   |           | Kartenname                     |
| battle_mode          | varchar(50)  | Ja   |           | Kampfmodus                     |
| battle_type          | varchar(50)  | Ja   |           | Kampftyp                       |
| battle_result        | varchar(10)  | Ja   |           | Kampfergebnis                  |
| battle_duration      | int          | Ja   |           | Kampfdauer in Sekunden         |
| trophy_change        | int          | Ja   |           | Gesamte Trophäenänderung      |
| rank                 | int          | Ja   |           | Platzierung (für Solo-Modi)    |
| is_star_player       | tinyint(1)   | Ja   |           | Star Player Status            |


## Verwendung

1. Server starten:
uvicorn main:app --reload

2. API-Endpunkte:
- `GET /battle-data`: Alle Battle Logs abrufen
- `GET /battle-data/{player_tag}`: Battle Logs eines bestimmten Spielers abrufen
- `GET /battle-data/{player_tag}/{battle_time}/{brawler_id}`: Spezifischen Battle Log abrufen
- `GET /battle-statistics`: Statistische Auswertung der Battle Logs
- `GET /trophy-progress`: Täglicher Trophy-Verlauf

3. API-Dokumentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Beispiel-Aufrufe

```bash
# Basis-Statistiken für einen Spieler
curl "http://localhost:8000/battle-statistics?player_tag=%232G9LP20YV0"

# Trophy-Verlauf für einen bestimmten Zeitraum
curl "http://localhost:8000/trophy-progress?player_tag=%232G9LP20YV0&start_date=2024-01-01T00:00:00&end_date=2024-03-14T23:59:59"

# Battle-Logs eines Spielers
curl "http://localhost:8000/battle-data/%232G9LP20YV0"
```

Hinweis: In URLs muss das #-Zeichen als %23 kodiert werden.
