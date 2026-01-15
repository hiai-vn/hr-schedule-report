import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telethon import TelegramClient
from src import config

def authenticate():
    print("Starting Telegram Authentication...")

    if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
        print("Error: TELEGRAM_API_ID or TELEGRAM_API_HASH not set in .env file.")
        print("Please create a .env file based on .env.example and fill in your credentials.")
        return

    # Initialize the client
    # The session file will be created in the root directory (or wherever the script is run from if not absolute)
    # We want it in the root, so we make sure it's handled relative to root.
    # config.SESSION_NAME defaults to "telegram_session"

    print(f"Connecting with API ID: {config.TELEGRAM_API_ID}...")

    client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)

    async def main():
        me = await client.get_me()
        print(f"\nSuccessfully logged in as: {me.first_name} (@{me.username})")
        print(f"Session file '{config.SESSION_NAME}.session' has been saved/updated.")

    # Start the client. This will launch the interactive login (phone number, code, password) if needed.
    client.start()
    client.loop.run_until_complete(main())

if __name__ == "__main__":
    authenticate()
