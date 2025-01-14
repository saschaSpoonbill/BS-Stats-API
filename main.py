from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, cast, Date

from database import SessionLocal, engine, Base
from models import BattleData
from schemas import BattleDataRead, BattleStatistics, TrophyProgressResponse, BrawlerStats, BrawlerStatsResponse, GameModeStats, GameModeStatsResponse

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


@app.get("/trophy-progress", response_model=TrophyProgressResponse)
def get_trophy_progress(
    player_tag: Optional[str] = None,
    start_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    end_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    db: Session = Depends(get_db)
):
    """
    Liefert den täglichen Trophy Progress. Optional gefiltert nach Spieler und Zeitraum.
    """
    # Basis-Filter erstellen
    filters = []
    if player_tag:
        filters.append(BattleData.player_tag == player_tag)
    if start_date:
        filters.append(BattleData.battle_time >= start_date)
    if end_date:
        filters.append(BattleData.battle_time <= end_date)

    # Victory-Bedingung (wie in get_battle_statistics)
    victory_condition = case(
        (BattleData.battle_mode == 'duoShowdown', BattleData.rank <= 2),
        (BattleData.battle_mode == 'soloShowdown', BattleData.rank <= 4),
        (BattleData.battle_mode.notin_(['duoShowdown', 'soloShowdown']), 
         BattleData.battle_result == 'victory')
    )

    # Tägliche Statistiken abfragen
    daily_stats = db.query(
        cast(BattleData.battle_time, Date).label('date'),
        func.sum(BattleData.trophy_change).label('trophy_change'),
        func.count().label('total_battles'),
        func.sum(case((victory_condition, 1), else_=0)).label('victory_count')
    ).filter(
        *filters
    ).group_by(
        cast(BattleData.battle_time, Date)
    ).order_by(
        cast(BattleData.battle_time, Date)
    ).all()

    if not daily_stats:
        raise HTTPException(status_code=404, detail="Keine Daten für den angegebenen Zeitraum gefunden.")

    # Gesamtstatistiken berechnen
    total_trophy_change = sum(day.trophy_change for day in daily_stats)
    total_battles = sum(day.total_battles for day in daily_stats)
    total_victories = sum(day.victory_count for day in daily_stats)

    # Tägliche Fortschritte formatieren
    daily_progress = [
        {
            "date": day.date,
            "trophy_change": day.trophy_change,
            "total_battles": day.total_battles,
            "victory_count": day.victory_count,
            "win_rate": round(day.victory_count / day.total_battles * 100, 2)
        }
        for day in daily_stats
    ]

    return {
        "player_tag": player_tag,
        "start_date": daily_stats[0].date,
        "end_date": daily_stats[-1].date,
        "daily_progress": daily_progress,
        "total_trophy_change": total_trophy_change,
        "total_battles": total_battles,
        "overall_win_rate": round(total_victories / total_battles * 100, 2)
    }


@app.get("/brawler-statistics", response_model=BrawlerStatsResponse)
def get_brawler_statistics(
    player_tag: Optional[str] = None,
    start_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    end_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    db: Session = Depends(get_db)
):
    """
    Liefert Statistiken für jeden verwendeten Brawler. Optional gefiltert nach Spieler und Zeitraum.
    """
    # Basis-Filter erstellen
    filters = []
    if player_tag:
        filters.append(BattleData.player_tag == player_tag)
    if start_date:
        filters.append(BattleData.battle_time >= start_date)
    if end_date:
        filters.append(BattleData.battle_time <= end_date)

    # Victory-Bedingung basierend auf battle_mode
    victory_condition = case(
        (BattleData.battle_mode == 'duoShowdown', BattleData.rank <= 2),
        (BattleData.battle_mode == 'soloShowdown', BattleData.rank <= 4),
        (BattleData.battle_mode.notin_(['duoShowdown', 'soloShowdown']), 
         BattleData.battle_result == 'victory')
    )

    # Statistiken pro Brawler abfragen mit COALESCE für NULL-Werte
    brawler_stats = db.query(
        BattleData.brawler_name,
        func.count().label('battles'),
        func.sum(case((victory_condition, 1), else_=0)).label('victories'),
        func.coalesce(func.sum(BattleData.trophy_change), 0).label('trophy_change')  # Behandelt NULL-Werte
    ).filter(
        *filters
    ).group_by(
        BattleData.brawler_name
    ).order_by(
        func.count().desc()  # Sortierung nach Anzahl Battles
    ).all()

    if not brawler_stats:
        raise HTTPException(status_code=404, detail="Keine Daten für den angegebenen Zeitraum gefunden.")

    # Gesamtstatistiken berechnen
    total_battles = sum(stat.battles for stat in brawler_stats)
    total_victories = sum(stat.victories for stat in brawler_stats)
    total_trophy_change = sum(stat.trophy_change or 0 for stat in brawler_stats)  # Sicherheit gegen NULL

    # Brawler-Statistiken formatieren
    brawler_statistics = [
        {
            "brawler_name": stat.brawler_name,
            "battles": stat.battles,
            "victories": stat.victories,
            "trophy_change": int(stat.trophy_change or 0),  # Konvertierung zu int und NULL-Handling
            "win_rate": round(stat.victories / stat.battles * 100, 2)
        }
        for stat in brawler_stats
    ]

    # Zeitraum ermitteln
    time_range = db.query(
        func.min(BattleData.battle_time).label('start_date'),
        func.max(BattleData.battle_time).label('end_date')
    ).filter(*filters).first()

    return {
        "player_tag": player_tag,
        "start_date": time_range.start_date,
        "end_date": time_range.end_date,
        "brawler_statistics": brawler_statistics,
        "total_battles": total_battles,
        "total_trophy_change": int(total_trophy_change),  # Konvertierung zu int
        "overall_win_rate": round(total_victories / total_battles * 100, 2)
    }


@app.get("/gamemode-statistics", response_model=GameModeStatsResponse)
def get_gamemode_statistics(
    player_tag: Optional[str] = None,
    start_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    end_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    db: Session = Depends(get_db)
):
    """
    Liefert Statistiken für jeden Game Mode. Optional gefiltert nach Spieler und Zeitraum.
    """
    # Basis-Filter erstellen
    filters = []
    if player_tag:
        filters.append(BattleData.player_tag == player_tag)
    if start_date:
        filters.append(BattleData.battle_time >= start_date)
    if end_date:
        filters.append(BattleData.battle_time <= end_date)

    # Victory-Bedingung basierend auf battle_mode
    victory_condition = case(
        (BattleData.battle_mode == 'duoShowdown', BattleData.rank <= 2),
        (BattleData.battle_mode == 'soloShowdown', BattleData.rank <= 4),
        (BattleData.battle_mode.notin_(['duoShowdown', 'soloShowdown']), 
         BattleData.battle_result == 'victory')
    )

    # Statistiken pro Game Mode abfragen
    gamemode_stats = db.query(
        BattleData.battle_mode,
        func.count().label('battles'),
        func.sum(case((victory_condition, 1), else_=0)).label('victories'),
        func.coalesce(func.sum(BattleData.trophy_change), 0).label('trophy_change'),
        func.avg(case(
            (BattleData.battle_duration.isnot(None), BattleData.battle_duration)
        )).label('avg_duration')
    ).filter(
        *filters
    ).group_by(
        BattleData.battle_mode
    ).order_by(
        func.count().desc()  # Sortierung nach Anzahl Battles
    ).all()

    if not gamemode_stats:
        raise HTTPException(status_code=404, detail="Keine Daten für den angegebenen Zeitraum gefunden.")

    # Gesamtstatistiken berechnen
    total_battles = sum(stat.battles for stat in gamemode_stats)
    total_victories = sum(stat.victories for stat in gamemode_stats)
    total_trophy_change = sum(stat.trophy_change or 0 for stat in gamemode_stats)

    # Game Mode Statistiken formatieren
    game_mode_statistics = []
    for stat in gamemode_stats:
        avg_trophies = round(stat.trophy_change / stat.battles, 2)
        
        # Berechne seconds_per_trophy nur wenn sowohl duration als auch trophy_change verfügbar
        seconds_per_trophy = None
        if stat.avg_duration and stat.trophy_change > 0:
            seconds_per_trophy = round((stat.avg_duration * stat.battles) / stat.trophy_change, 2)

        game_mode_statistics.append({
            "battle_mode": stat.battle_mode,
            "battles": stat.battles,
            "victories": stat.victories,
            "trophy_change": int(stat.trophy_change or 0),
            "avg_duration": round(stat.avg_duration, 2) if stat.avg_duration else None,
            "avg_trophies_per_battle": avg_trophies,
            "seconds_per_trophy": seconds_per_trophy,
            "win_rate": round(stat.victories / stat.battles * 100, 2)
        })

    # Zeitraum ermitteln
    time_range = db.query(
        func.min(BattleData.battle_time).label('start_date'),
        func.max(BattleData.battle_time).label('end_date')
    ).filter(*filters).first()

    return {
        "player_tag": player_tag,
        "start_date": time_range.start_date,
        "end_date": time_range.end_date,
        "game_mode_statistics": game_mode_statistics,
        "total_battles": total_battles,
        "total_trophy_change": int(total_trophy_change),
        "overall_win_rate": round(total_victories / total_battles * 100, 2)
    }
