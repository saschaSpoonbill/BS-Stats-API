from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Gemeinsame Felder in allen Schemas
class BattleDataBase(BaseModel):
    player_tag: str
    battle_time: datetime
    brawler_id: int

    brawler_name: Optional[str] = None
    brawler_power: Optional[int] = None
    brawler_trophies: Optional[int] = None
    brawler_trophy_change: Optional[int] = None
    player_name: Optional[str] = None
    event_id: Optional[int] = None
    event_mode: Optional[str] = None
    event_map: Optional[str] = None
    battle_mode: Optional[str] = None
    battle_type: Optional[str] = None
    battle_result: Optional[str] = None
    battle_duration: Optional[int] = None
    trophy_change: Optional[int] = None
    rank: Optional[int] = None
    is_star_player: Optional[bool] = None


# Schema zum Auslesen (ORM-Unterstützung aktivieren)
class BattleDataRead(BattleDataBase):
    class Config:
        orm_mode = True
