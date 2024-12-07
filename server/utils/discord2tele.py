import datetime
import json
import random
from datetime import datetime, timedelta

# Load the input JSON from a file
input_file = "discord_channels.json"
output_file = "telegram_channels.json"

# Function to generate random timestamp
def random_date(start, end):
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

# Load the JSON data from the file
with open(input_file, "r") as infile:
    input_data = json.load(infile)

# Define the range for random timestamp generation
start_date = datetime(2020, 10, 1)
end_date = datetime(2024, 12, 1)

# Define some channel names
channel_names = ["FishingHub", "TechTalk", "RandomChat", "GamingHub", "OutdoorAdventures"]

# Transform data
output_data = {
    "about": "Here is the data you requested. Remember: Telegram is ad free, it doesn't use your data for ad targeting and doesn't sell it to others. Telegram only keeps the information it needs to function as a secure and feature-rich cloud service.\n\nCheck out Settings > Privacy & Security on Telegram's mobile apps for the relevant settings.",
    "chats": {
        "about": "This page lists all chats from this export.",
        "list": []
    }
}

# Initialize a global counter for unique IDs
global_id_counter = 1

# Randomly assign messages to different channels
channels = {name: [] for name in channel_names}
for chat in input_data['chats']['list']:
    for message in chat['messages']:
        timestamp = random_date(start_date, end_date).isoformat()
        channel = random.choice(channel_names)
        channels[channel].append({
            "id": global_id_counter,
            "type": "service" if "Joined the server" in message['text'] else "message",
            "date": timestamp,
            "from": message['username'],
            "from_id": f"channel{random.randint(100000000, 999999999)}",
            "text": message['text']
        })
        global_id_counter += 1

# Add channels to output structure
for channel_name, messages in channels.items():
    if messages:  # Only include channels with messages
        output_data["chats"]["list"].append({
            "name": channel_name,
            "type": "private_channel",
            "id": random.randint(1000000000, 9999999999),
            "messages": messages
        })

# Save the transformed data to the output JSON file
with open(output_file, "w") as outfile:
    json.dump(output_data, outfile, indent=2)

print(f"Data has been transformed and saved to {output_file}.")
