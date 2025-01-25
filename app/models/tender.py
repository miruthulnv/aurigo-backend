from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .base import Base
db = SQLAlchemy()

class Tender(Base):
    __tablename__ = 'tenders'

    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    publish_date = db.Column(db.DateTime, nullable=False)
    closing_date = db.Column(db.DateTime, nullable=False)
    estimated_value = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    requirements = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def __init__(self, id, title, description, publish_date, closing_date, estimated_value, currency, category, requirements, status):
        self.id = id
        self.title = title
        self.description = description
        self.publish_date = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ")
        self.closing_date = datetime.strptime(closing_date, "%Y-%m-%dT%H:%M:%SZ")
        self.estimated_value = estimated_value
        self.currency = currency
        self.category = category
        self.requirements = requirements
        self.status = status

    def __repr__(self):
        return f"<Tender {self.title}>"
