import json
import random
from datetime import datetime, timedelta

# Generate random date within the specified range
def generate_random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86400)  # Random seconds in a day
    return start_date + timedelta(days=random_days, seconds=random_seconds)

# Parse human_chat.txt for messages
def parse_human_chat(file_path):
    human1_messages = []
    human2_messages = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.strip():  # Skip empty lines
                user, text = line.split(":", 1)
                if user.strip() == "Human 1":
                    human1_messages.append(text.strip())
                elif user.strip() == "Human 2":
                    human2_messages.append(text.strip())
    return human1_messages, human2_messages

# Generate messages with global integer IDs
def generate_messages(messages, start_date, end_date, chat_offset):
    chat_messages = []
    for i, text in enumerate(messages, 1):
        date = generate_random_date(start_date, end_date)
        global_id = chat_offset + i  # Create a unique integer ID by adding an offset
        message = {
            "id": global_id,  # Use the globally unique integer ID
            "type": "message",
            "date": date.strftime("%Y-%m-%dT%H:%M:%S"),
            "from": "user",  # Since each chat is by one user, "from" can be generic
            "from_id": f"user{random.randint(1000000000, 9999999999)}",
            "text": text
        }
        chat_messages.append(message)
    return chat_messages

# Generate a chat dataset with global message IDs
def generate_chat_dataset(human1_messages, human2_messages, start_date, end_date):
    chat_data = {
        "about": "Here is the data you requested. Remember: Telegram is ad free, it doesn't use your data for ad targeting and doesn't sell it to others. Telegram only keeps the information it needs to function as a secure and feature-rich cloud service.\n\nCheck out Settings > Privacy & Security on Telegram's mobile apps for the relevant settings.",
        "chats": {
            "about": "This page lists all chats from this export.",
            "list": [
                {
                    "name": "Human 1",
                    "type": "personal_chat",
                    "id": "7777774701",
                    "messages": generate_messages(human1_messages, start_date, end_date, chat_offset=1000000)
                },
                {
                    "name": "Human 2",
                    "type": "personal_chat",
                    "id": "7777774702",
                    "messages": generate_messages(human2_messages, start_date, end_date, chat_offset=2000000)
                }
            ]
        }
    }
    return chat_data

# Save dataset to a JSON file
def save_dataset_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Main function to generate and save dataset
if __name__ == "__main__":
    input_file = "human_chat.txt"  # Replace with your actual file path
    start_date = datetime(2022, 2, 1)
    end_date = datetime(2024, 11, 26)
    
    # Read and parse chat file
    human1_messages, human2_messages = parse_human_chat(input_file)
    
    # Generate dataset
    dataset = generate_chat_dataset(human1_messages, human2_messages, start_date, end_date)
    
    # Save dataset to JSON
    save_dataset_to_json(dataset, "telegram_chat_history.json")
    print("Chat history saved to telegram_chat_history.json")
