import sys
import os
import asyncio

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telethon import TelegramClient
from src import config
from src import collector

def main():
    if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
        print("Error: TELEGRAM_API_ID or TELEGRAM_API_HASH not set.")
        return

    print("Initializing Telegram Client...")
    # config.SESSION_NAME is just the name (e.g. 'telegram_session'), Telethon appends .session
    # We rely on the session file created by telegram_auth.py being in the current working directory or handled correctly.
    # Since we run from root usually, it should be fine.
    client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)

    async def run_collection():
        print("Starting data collection...")
        messages = await collector.fetch_messages(client)

        if messages:
            output_file = os.path.join("data", "raw_messages.json")
            collector.save_to_json(messages, output_file)
        else:
            print("No messages collected.")

    # Start the client. This will use the existing session file.
    # If not authorized, it might block waiting for input, but in a script environment intended for automation,
    # we assume auth is done.
    client.start()
    client.loop.run_until_complete(run_collection())

if __name__ == "__main__":
    main()
