import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Lade Umgebungsvariablen aus .env
load_dotenv()

# Hole Database URL aus Umgebungsvariablen
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "Keine DATABASE_URL in Umgebungsvariablen gefunden. "
        "Bitte .env Datei mit DATABASE_URL erstellen."
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()