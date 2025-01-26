from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base
from datetime import datetime


class Bid(Base):
    __tablename__ = 'bids'

    id = Column(Integer, primary_key=True)
    bidder_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_name = Column(String(255), nullable=False)
    bid_cost = Column(Float, nullable=False)
    proposed_timeline = Column(Integer, nullable=False)  # in days
    tender_id = Column(String, ForeignKey('tenders.id'), nullable=False)
    overall_score = Column(Integer,nullable=True)
    readable_insights = Column(String,nullable=True)
    # Relationships
    # Matching string-based relationship
    bidder = relationship("User", back_populates="bids")
    tender = relationship("Tender", back_populates="bids")

    def __init__(self, bidder_id, company_name, bid_cost, proposed_timeline, tender_id):
        self.bidder_id = bidder_id
        self.company_name = company_name
        self.bid_cost = bid_cost
        self.proposed_timeline = proposed_timeline
        self.tender_id = tender_id

    def __repr__(self):
        return f"<Bid(id={self.id}, bidder_id={self.bidder_id}, company_name='{self.company_name}', bid_cost={self.bid_cost}, proposed_timeline={self.proposed_timeline} days)>"

