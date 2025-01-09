from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base

class BattleData(Base):
    __tablename__ = "battle_logs"
    
    player_tag = Column(String(50), primary_key=True)
    battle_time = Column(DateTime, primary_key=True)
    brawler_id = Column(Integer, primary_key=True)

    brawler_name = Column(String(50))
    brawler_power = Column(Integer)
    brawler_trophies = Column(Integer)
    brawler_trophy_change = Column(Integer)
    player_name = Column(String(50))
    event_id = Column(Integer)
    event_mode = Column(String(50))
    event_map = Column(String(100))
    battle_mode = Column(String(50))
    battle_type = Column(String(50))
    battle_result = Column(String(10))
    battle_duration = Column(Integer)
    trophy_change = Column(Integer)
    rank = Column(Integer)
    is_star_player = Column(Boolean)
