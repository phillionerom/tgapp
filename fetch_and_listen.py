from telegram_client import start_client

# Telegram @usernames or channel IDs
CHANNELS = ["liquidaciones"]


if __name__ == "__main__":
    start_client(CHANNELS)
