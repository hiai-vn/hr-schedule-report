import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telethon import TelegramClient
from telethon.tl.types import Channel
from src import config

def get_dialog_info():
    if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
        print("Error: TELEGRAM_API_ID or TELEGRAM_API_HASH not set.")
        return

    print("Connecting to Telegram...")
    client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)

    async def main():
        print("\n--- Fetching Dialogs (Groups/Channels) ---")
        print("This may take a moment...")

        # Get dialogs
        dialogs = await client.get_dialogs()

        print(f"Found {len(dialogs)} dialogs.\n")

        for d in dialogs:
            # We are mostly interested in Groups and Channels
            if d.is_group or d.is_channel:
                print(f"Name: {d.name}")
                print(f"ID: {d.id}")

                # Check for topics if it is a forum
                entity = d.entity
                if isinstance(entity, Channel) and entity.forum:
                    print("  [This is a Forum. Fetching Topics...]")
                    try:
                        # get_forum_topics
                        topics = await client.get_forum_topics(entity)
                        if topics:
                            for topic in topics:
                                 print(f"    - Topic: {topic.title} | ID: {topic.id}")
                        else:
                            print("    (No topics found)")
                    except Exception as e:
                        print(f"    (Could not fetch topics: {e})")

                print("-" * 40)

        print("\n--- End of List ---")
        print("Copy the Group ID and Topic ID (if applicable) to your .env file.")

    client.start()
    client.loop.run_until_complete(main())

if __name__ == "__main__":
    get_dialog_info()
