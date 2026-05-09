import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import chromadb
from chromadb.config import Settings

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
SQL_DB_PATH = os.path.join(DATA_DIR, "insights_assistant.db")
CHROMA_PATH = os.path.join(DATA_DIR, "chroma_db")

# SQL Database Configuration
SQL_ENGINE = create_engine(f"sqlite:///{SQL_DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=SQL_ENGINE)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_vector_client():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client

def init_dbs():
    # Initialize SQL tables
    Base.metadata.create_all(bind=SQL_ENGINE)
    print(f"SQL DB initialized at {SQL_DB_PATH}")
    
    # Initialize Vector DB
    client = get_vector_client()
    print(f"ChromaDB initialized at {CHROMA_PATH}")

if __name__ == "__main__":
    init_dbs()
