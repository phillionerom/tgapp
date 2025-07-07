from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///db.sqlite3"  # Cambiar por postgres://user:pass@host/dbname

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función para obtener mensajes no publicados
def get_unposted_messages(limit=10):
    from OLD.messages import ParsedMessage  # importar aquí para evitar ciclos
    db = SessionLocal()
    try:
        return db.query(ParsedMessage).filter_by(posted=False).limit(limit).all()
    finally:
        db.close()

# Función para marcar como publicado
def mark_as_posted(message_id: int, channel: str):
    from OLD.messages import ParsedMessage
    db = SessionLocal()
    try:
        msg = db.query(ParsedMessage).filter_by(message_id=message_id, channel=channel).first()
        if msg:
            msg.posted = True
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Error al marcar como publicado: {e}")
    finally:
        db.close()