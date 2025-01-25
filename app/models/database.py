from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .user import User
from .tender import Tender
from .base import Base
from contextlib import contextmanager
from sqlalchemy.orm import configure_mappers
from app.models.user import User
from app.models.bids import Bid


# Initialize SQLite database
engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)
configure_mappers()

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
