from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .user import User
from .tender import Tender
from .company import Company
from .base import Base

# Initialize SQLite database
engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Verify that tables are created
print(engine.table_names())
