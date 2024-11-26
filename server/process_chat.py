import json
import psycopg2 as pg
from datetime import datetime
from tqdm import tqdm
import sys

def load_data_to_database(json_path):
    conn = None
    cursor = None
    try:
        conn = pg.connect(
            dbname="chats",
            user="postgres",
            password="1234",
            host="localhost",
            port=5432
        )
        cursor = conn.cursor()
        print("Database connection successful!", file=sys.stderr)

        # Create the 'messages' table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id SERIAL PRIMARY KEY,
                chat_id VARCHAR(255) NOT NULL,
                sender VARCHAR(255),
                sender_id VARCHAR(255),
                text TEXT,
                time TIMESTAMP NOT NULL,
                reply_to_message_id INT,
                chat_contact VARCHAR(255)
            )
        """)
        conn.commit()
        print("Table 'messages' ensured to exist.", file=sys.stderr)

        # Load the JSON data
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chats_list = data.get("chats", {}).get("list", [])
        contacts = []
        for chats in chats_list:
            chat_contact = chats.get("name")
            chat_id = chats.get("id")
            contacts.append(chat_contact)
            print(f"Processing the chat with {chat_contact}...", file=sys.stderr)

            for message in tqdm(chats.get("messages", [])):
                text = message.get("text")
                if text and not message.get("forwarded_from") and isinstance(text, str):
                    message_id = message.get("id")
                    sender = message.get("from")
                    sender_id = message.get("from_id")
                    reply_to_message_id = message.get("reply_to_message_id", -1)
                    timestamp = datetime.fromisoformat(message.get("date"))

                    cursor.execute("""
                        INSERT INTO messages (message_id, chat_id, sender, 
                        sender_id, text, time, reply_to_message_id, chat_contact)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, 
                        (message_id, chat_id, sender, sender_id, text, timestamp, reply_to_message_id, chat_contact)
                    )

        conn.commit()
        print("Data committed to database successfully.", file=sys.stderr)
        return contacts
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    json_path = sys.argv[1]  # "../client/data/telegram_chats.json" #
    contacts = load_data_to_database(json_path)
    print(json.dumps(contacts))
