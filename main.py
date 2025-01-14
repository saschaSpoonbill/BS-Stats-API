from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_

from database import SessionLocal, engine, Base
from models import BattleData
from schemas import BattleDataRead, BattleStatistics

# Erzeugt Tabellen in der Datenbank (falls nicht bereits vorhanden)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency für die DB-Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/battle-data", response_model=List[BattleDataRead])
def read_all_battle_data(db: Session = Depends(get_db)):
    """Liest alle BattleData-Einträge aus."""
    return db.query(BattleData).all()


@app.get("/battle-data/{player_tag}", response_model=List[BattleDataRead])
def read_battle_data_by_player(player_tag: str, db: Session = Depends(get_db)):
    """Liest alle BattleData-Einträge eines bestimmten Spielers anhand des player_tag."""
    results = db.query(BattleData).filter(BattleData.player_tag == player_tag).all()
    if not results:
        raise HTTPException(status_code=404, detail="Keine Einträge für diesen Player gefunden.")
    return results


@app.get("/battle-data/{player_tag}/{battle_time}/{brawler_id}", response_model=BattleDataRead)
def read_one_battle_data(player_tag: str, battle_time: str, brawler_id: int, db: Session = Depends(get_db)):
    """
    Liest einen einzelnen BattleData-Eintrag anhand des zusammengesetzten Primärschlüssels.
    Erwartet battle_time als String im ISO-Format, z. B. '2023-05-06T15:30:00'.
    """
    entry = db.query(BattleData).filter(
        BattleData.player_tag == player_tag,
        BattleData.battle_time == battle_time,
        BattleData.brawler_id == brawler_id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Keine Daten für diese Parameter gefunden.")
    return entry


@app.get("/battle-statistics", response_model=BattleStatistics)
def get_battle_statistics(
    player_tag: Optional[str] = None,
    start_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    end_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    db: Session = Depends(get_db)
):
    """
    Liefert Statistiken über Battle Logs. Optional gefiltert nach Spieler und Zeitraum.
    """
    # Basis-Filter erstellen
    filters = []
    if player_tag:
        filters.append(BattleData.player_tag == player_tag)
    if start_date:
        filters.append(BattleData.battle_time >= start_date)
    if end_date:
        filters.append(BattleData.battle_time <= end_date)

    # Basis-Statistiken mit Filtern
    stats = db.query(
        func.min(BattleData.battle_time).label('first_battle'),
        func.max(BattleData.battle_time).label('last_battle'),
        func.count().label('total_battles'),
        func.count(func.distinct(BattleData.player_tag)).label('unique_players')
    ).filter(*filters).first()

    # Wenn keine Daten gefunden wurden
    if not stats.first_battle:
        raise HTTPException(status_code=404, detail="Keine Battles im angegebenen Zeitraum gefunden.")

    # Berechne Tage zwischen erstem und letztem Battle
    days_diff = (stats.last_battle - stats.first_battle).days + 1

    # Victory-Bedingung basierend auf battle_mode
    victory_condition = case(
        (BattleData.battle_mode == 'duoShowdown', BattleData.rank <= 2),
        (BattleData.battle_mode == 'soloShowdown', BattleData.rank <= 4),
        (BattleData.battle_mode.notin_(['duoShowdown', 'soloShowdown']), 
         BattleData.battle_result == 'victory')
    )

    # Erweiterte Statistiken mit denselben Filtern
    extended_stats = db.query(
        func.sum(case((victory_condition, 1), else_=0)).label('victories'),
        func.sum(BattleData.trophy_change).label('total_trophies')
    ).filter(*filters).first()

    return {
        "first_battle": stats.first_battle,
        "last_battle": stats.last_battle,
        "total_battles": stats.total_battles,
        "unique_players": stats.unique_players,
        "avg_battles_per_day": round(stats.total_battles / days_diff, 2),
        "avg_trophies_per_day": round(extended_stats.total_trophies / days_diff, 2),
        "avg_victories_per_day": round(extended_stats.victories / days_diff, 2),
        "win_rate": round(extended_stats.victories / stats.total_battles * 100, 2)
    }
