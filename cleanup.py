from db.db import delete_messages_older_than
from datetime import datetime, timedelta


def clean_old_messages(days=30):
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    delete_messages_older_than(cutoff_date)

if __name__ == "__main__":
    clean_old_messages()