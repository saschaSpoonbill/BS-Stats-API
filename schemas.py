from datetime import datetime
from typing import Optional, List
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

    class Config:
        from_attributes = True

# Schema zum Auslesen (ORM-Unterstützung aktivieren)
class BattleDataRead(BattleDataBase):
    class Config:
        from_attributes = True

class BattleStatistics(BaseModel):
    first_battle: datetime
    last_battle: datetime
    total_battles: int
    unique_players: int
    avg_battles_per_day: float
    avg_trophies_per_day: float
    avg_victories_per_day: float
    win_rate: float

    class Config:
        from_attributes = True

class DailyTrophyProgress(BaseModel):
    date: datetime
    trophy_change: int
    total_battles: int
    victory_count: int
    win_rate: float

    class Config:
        from_attributes = True

class TrophyProgressResponse(BaseModel):
    player_tag: Optional[str] = None
    start_date: datetime
    end_date: datetime
    daily_progress: List[DailyTrophyProgress]
    total_trophy_change: int
    total_battles: int
    overall_win_rate: float

    class Config:
        from_attributes = True

class BrawlerStats(BaseModel):
    brawler_name: str
    battles: int
    victories: int
    trophy_change: int
    win_rate: float

    class Config:
        from_attributes = True

class BrawlerStatsResponse(BaseModel):
    player_tag: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    brawler_statistics: List[BrawlerStats]
    total_battles: int
    total_trophy_change: int
    overall_win_rate: float

    class Config:
        from_attributes = True

class GameModeStats(BaseModel):
    battle_mode: str
    battles: int
    victories: int
    trophy_change: int
    avg_duration: Optional[float] = None  # in Sekunden
    avg_trophies_per_battle: float
    seconds_per_trophy: Optional[float] = None
    win_rate: float

    class Config:
        from_attributes = True

class GameModeStatsResponse(BaseModel):
    player_tag: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    game_mode_statistics: List[GameModeStats]
    total_battles: int
    total_trophy_change: int
    overall_win_rate: float

    class Config:
        from_attributes = True
