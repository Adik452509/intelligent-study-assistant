from sqlalchemy import  create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class StudySession(Base):
    """Track individual study sessions"""
    __tablename__ = 'study_sessions'

    id = Column(Integer, primary_key=True)
    topic = Column(String(200), nullable=False)
    topic = Column(String(200), nullable=False)
    duration_minutes = Column(Float, nullable=False)
    completed = Column(Boolean, default=False)
    date = Column(DateTime, default=datetime.now)
    notes = Column(Text)
    difficulty_rating = Column(Integer)  # 1-5 scale
    focus_level = Column(Integer)  # 1-10

#database initialization
def init_database():
    engine = create_engine('sqlite:///study_assistant.db')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal

def get_db():
    SessionLocal = init_database()
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("✅ Database initialized!")    
    
      