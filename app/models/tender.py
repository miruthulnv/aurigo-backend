from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .base import Base
db = SQLAlchemy()

class Tender(Base):
    __tablename__ = 'tenders'

    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    est_cost = db.Column(db.Float, nullable=False)
    est_timeline = db.Column(db.Integer, nullable=False)
    cost_weight = db.Column(db.Float, nullable=False)
    timeline_weight = db.Column(db.Float, nullable=False)
    compliance_weight = db.Column(db.Float, nullable=False)
    current_factors_weight = db.Column(db.Float, nullable=False)
    historical_rating_weight = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    publish_date = db.Column(db.String, nullable=False)
    closing_date = db.Column(db.String, nullable=False)
    bids = db.relationship("Bid", back_populates="tender")
    status = db.Column(db.String(20), nullable=False)

    def __init__(
            self,
            id,
            title,
            department,
            description,
            est_cost,
            est_timeline,
            cost_weight,
            timeline_weight,
            compliance_weight,
            current_factors_weight,
            historical_rating_weight,
            currency,
            email,
            category,
            publish_date,
            closing_date,
            status
    ):
        self.id = id
        self.title = title
        self.department = department
        self.description = description
        self.est_cost = est_cost
        self.est_timeline = est_timeline
        self.cost_weight = cost_weight
        self.timeline_weight = timeline_weight
        self.compliance_weight = compliance_weight
        self.current_factors_weight = current_factors_weight
        self.historical_rating_weight = historical_rating_weight
        self.currency = currency
        self.email = email
        self.category = category
        # self.publish_date = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")
        # self.closing_date = datetime.strptime(closing_date, "%Y-%m-%dT%H:%M:%SZ")
        if isinstance(publish_date, str):
            self.publish_date = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(publish_date, datetime):
            self.publish_date = publish_date
        else:
            raise TypeError("publish_date must be a string in ISO format or a datetime object")

            # Same logic for closing_date
        if isinstance(closing_date, str):
            self.closing_date = datetime.strptime(closing_date, "%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(closing_date, datetime):
            self.closing_date = closing_date
        else:
            raise TypeError("closing_date must be a string in ISO format or a datetime object")

        self.status = status

    def __repr__(self):
        return f"<Tender {self.id}>"