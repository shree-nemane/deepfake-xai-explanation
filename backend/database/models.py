from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import uuid

Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String)
    prediction = Column(String)
    confidence = Column(Float)
    uncertainty = Column(String)
    risk_score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    model_version = Column(String)
    rule_version = Column(String)
    
    # Store complex XAI data as JSON
    xai_data = Column(JSON)
    
    evidence = relationship("Evidence", back_populates="report", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String, ForeignKey("reports.id"))
    feature_name = Column(String)
    value = Column(Float)
    anomaly_score = Column(Float)
    
    report = relationship("Report", back_populates="evidence")
