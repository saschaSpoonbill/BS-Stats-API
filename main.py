from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import BattleData
from schemas import BattleDataRead

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
