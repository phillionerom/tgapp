from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

from datetime import datetime

Base = declarative_base()


class ParsedMessage(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, index=True)  # id en telegram
    date = Column(DateTime, default=datetime.utcnow)
    channel = Column(String, index=True)
    title = Column(String)
    content = Column(String)
    more_info = Column(String)
    offer_price = Column(Float)
    normal_price = Column(Float)
    savings_percent = Column(Float)
    message_url = Column(String)
    short_url = Column(String)
    product_code = Column(String)
    product_url = Column(String)
    image = Column(String)
    category = Column(String)
    posted = Column(Boolean, default=False)

class Publication(Base):
    __tablename__ = 'publications'

    id = Column(Integer, primary_key=True)
    message_id = Column(String, ForeignKey("messages.id"))
    channel = Column(String)
    published_at = Column(DateTime, default=func.now())

    message = relationship("Message", back_populates="published")
