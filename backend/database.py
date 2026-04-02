from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

engine = create_engine(f"sqlite:///{config.DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TrafficResult(Base):
    __tablename__ = "traffic_results"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_id = Column(String, index=True)
    frame_id = Column(Integer)
    vehicle_count = Column(Integer)
    congestion_level = Column(String)
    avg_speed = Column(String)  # Serialized list or single value
    flow_rate = Column(Integer)  # Vehicles per minute
    density = Column(Integer)
    total_lane_changes = Column(Integer)
    fps = Column(String)
    latency = Column(String)
    predicted_count = Column(Integer)
    predicted_congestion = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
