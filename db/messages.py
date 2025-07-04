from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from datetime import datetime

DATABASE_URL = "sqlite:///db.sqlite3"  # cambiar facilmente a PostgreSQL, etc

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
    coupon = Column(String)
    message_url = Column(String)
    short_url = Column(String)
    product_code = Column(String)
    product_url = Column(String)
    image = Column(String)
    category = Column(String)
    posted = Column(Boolean, default=False)

# Crear la tabla si no existe
Base.metadata.create_all(bind=engine)

# Helper para guardar un mensaje

def save_parsed_message(data: dict):
    session = SessionLocal()
    try:
        exists = session.query(ParsedMessage).filter_by(message_id=data["id"], channel=data["channel"]).first()
        if exists:
            print("🔁 Mensaje ya existe en la base de datos")
            return False

        msg = ParsedMessage(
            message_id=data["id"],
            date=datetime.fromisoformat(data["date"]),
            channel=data["channel"],
            title=data["title"],
            content=data["content"],
            more_info=data["more_info"],
            offer_price=data["offer_price"],
            normal_price=data["normal_price"],
            savings_percent=data["savings_percent"],
            coupon=data["coupon"],
            message_url=data["message_url"],
            short_url=data["short_url"],
            product_code=data["product_code"],
            product_url=data["product_url"],
            image=data["image"],
            category=data["category"]
        )
        session.add(msg)
        session.commit()
        print("✅ Parsed message stored in db successfully")
        return True
    except Exception as e:
        print(f"❌ Error while storing message in db: {e}")
        session.rollback()
        return False
    finally:
        session.close()
