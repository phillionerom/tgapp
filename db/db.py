from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exists
from datetime import datetime, timedelta

from config import DATABASE_URL
from db.models import Base, ParsedMessage

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def message_exists(message_id, channel):
    session = Session()
    try:
        return session.query(
            exists().where(
                (ParsedMessage.message_id == message_id) &
                (ParsedMessage.channel == channel)
            )
        ).scalar()
    finally:
        session.close()

def save_message(data):
    session = Session()
    try:
        if not message_exists(data["message_id"], data["channel"]):
            msg = ParsedMessage(
                message_id=data["message_id"],
                date=data.get("date", datetime.utcnow()),
                channel=data["channel"],
                title=data.get("title"),
                content=data.get("content"),
                more_info=data.get("more_info"),
                offer_price=data.get("offer_price"),
                normal_price=data.get("normal_price"),
                savings_percent=data.get("savings_percent"),
                message_url=data.get("message_url"),
                short_url=data.get("short_url"),
                product_code=data.get("product_code"),
                product_url=data.get("product_url"),
                image=data.get("image"),
                category=data.get("category"),
                posted=False
            )
            session.add(msg)
            session.commit()
            
    finally:
        session.close()

def get_unpublished_messages():
    session = Session()
    try:
        msgs = session.query(ParsedMessage).filter_by(posted=False).all()
        return [msg_to_dict(m) for m in msgs]
    finally:
        session.close()

def mark_as_posted(msg_id):
    session = Session()
    try:
        msg = session.query(ParsedMessage).filter_by(id=msg_id).first()
        if msg:
            msg.posted = True
            session.commit()
    finally:
        session.close()

def delete_old_messages(days=30):
    session = Session()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        session.query(ParsedMessage).filter(ParsedMessage.date < cutoff).delete()
        session.commit()
    finally:
        session.close()

def msg_to_dict(msg):
    return {
        "id": msg.id,
        "message_id": msg.message_id,
        "date": msg.date,
        "channel": msg.channel,
        "title": msg.title,
        "content": msg.content,
        "more_info": msg.more_info,
        "offer_price": msg.offer_price,
        "normal_price": msg.normal_price,
        "savings_percent": msg.savings_percent,
        "message_url": msg.message_url,
        "short_url": msg.short_url,
        "product_code": msg.product_code,
        "product_url": msg.product_url,
        "image": msg.image,
        "category": msg.category,
        "posted": msg.posted
    }
