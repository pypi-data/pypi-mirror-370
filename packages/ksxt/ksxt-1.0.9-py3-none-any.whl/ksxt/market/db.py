from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Market(Base):
    __tablename__ = "market"

    # Market Code
    code = Column(String, primary_key=True)

    # Market Name
    name = Column(String, nullable=False)

    # Sync time
    sync_at = Column(DateTime, nullable=True)
