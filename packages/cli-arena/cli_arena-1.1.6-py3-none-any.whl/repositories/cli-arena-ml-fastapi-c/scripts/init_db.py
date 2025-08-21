import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.makedirs('db', exist_ok=True)
from sqlalchemy import create_engine
from src.behavior_analysis.models import Base as BA_Base
from src.instagram_api.models import Base as IG_Base

def main():
    db_url = os.getenv('SATURN_DB_URL', 'sqlite:///db/saturn.db')
    engine = create_engine(db_url)
    print(f"Creating all tables at {db_url}...")
    BA_Base.metadata.create_all(engine)
    IG_Base.metadata.create_all(engine)
    print("Database initialized.")

if __name__ == '__main__':
    main() 