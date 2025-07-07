from OLD.session import Base, engine
from OLD.messages import ParsedMessage

def init():
    print("🧱 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Done.")

if __name__ == "__main__":
    init()
