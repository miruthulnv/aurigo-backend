from sqlalchemy import Column, Integer, String, Float, Date, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from .base import Base

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    years_of_experience = Column(Integer, nullable=False)
    credit_score = Column(Float)
    financial_stability_score = Column(Float)
    projects_completed = Column(Integer)
    average_client_rating = Column(Float)
    success_rate = Column(Float)
    location = Column(String(255))
    regional_experience_score = Column(Float)
    current_workload = Column(Integer)
    legal_disputes_count = Column(Integer)
    safety_incidents_count = Column(Integer)
    sustainability_score = Column(Float)
    technology_adoption_score = Column(Float)
    additional_benefits = Column(JSON)
    overall_score = Column(Float)

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.full_name}', overall_score={self.overall_score})>"