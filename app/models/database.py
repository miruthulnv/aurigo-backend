from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .user import User
from .tender import Tender
from .company import Company
from .base import Base
from contextlib import contextmanager

# Initialize SQLite database
engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# Verify that tables are created
