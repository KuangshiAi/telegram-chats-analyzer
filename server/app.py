from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import psycopg2 as pg
from datetime import datetime
from tqdm import tqdm
import threading
import pandas as pd
from utils.generate_calendar import generate_calendar


app = Flask(__name__)
CORS(app)

TEMP_JSON_PATH = "./uploads/temp.json"

progress = {"total_contacts": 0, "processed_contacts": 0, "current_contact_progress": 0}


# Database connection parameters
DB_PARAMS = {
    "dbname": "chats",
    "user": "postgres",
    "password": "5623242",
    "host": "localhost",
    "port": 5432,
}


def get_db_connection():
    conn = pg.connect(**DB_PARAMS)
    return conn


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if file and file.filename.endswith(".json"):
        file.save(TEMP_JSON_PATH)
        # Initialize progress
        progress["total_contacts"] = 0
        progress["processed_contacts"] = 0
        progress["current_contact_progress"] = 0
        return (
            jsonify({"message": "File uploaded successfully. Ready for processing."}),
            200,
        )
    return jsonify({"message": "Invalid file type."}), 400


@app.route("/process", methods=["POST"])
def process_data():
    # Get the table name from the request data
    data = request.get_json()
    table_name = data.get("tableName")

    # Start a new thread to process the data to avoid blocking the request
    threading.Thread(target=load_data_to_database, args=(TEMP_JSON_PATH, table_name)).start()
    return jsonify({"message": "Data processing started."}), 200

def load_data_to_database(json_path, table_name="messages2"):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the table exists, if not create it with the specified format
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            message_id BIGINT,
            chat_id TEXT,
            chat_contact TEXT,
            sender TEXT,
            sender_id TEXT,
            text TEXT,
            time TIMESTAMP WITHOUT TIME ZONE,
            reply_to_message_id BIGINT
        )
    """)
    conn.commit()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    chats_list = data.get("chats").get("list")
    total_contacts = len(chats_list)
    progress["total_contacts"] = total_contacts
    progress["processed_contacts"] = 0

    for chats in chats_list:
        chat_contact = chats.get("name")
        chat_id = chats.get("id")
        messages = chats.get("messages")
        total_messages = len(messages)
        progress["current_contact_progress"] = 0

        for message_index, message in enumerate(messages):
            text = message.get("text")
            if text and not message.get("forwarded_from") and isinstance(text, str):
                message_id = message.get("id")
                sender = message.get("from")
                sender_id = message.get("from_id")
                reply_to_message_id = message.get("reply_to_message_id", -1)
                timestamp = datetime.fromisoformat(message.get("date"))
                cursor.execute(
                    f"""
                    INSERT INTO {table_name} (message_id, chat_id, sender, 
                    sender_id, text, time, reply_to_message_id, chat_contact)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        message_id,
                        chat_id,
                        sender,
                        sender_id,
                        text,
                        timestamp,
                        reply_to_message_id,
                        chat_contact,
                    ),
                )
            # Update current contact progress
            progress["current_contact_progress"] = (
                int(((message_index + 1) / total_messages) * 10000) / 100
            )
        # Mark this contact as processed
        progress["processed_contacts"] += 1

    conn.commit()
    cursor.close()
    conn.close()


@app.route("/progress", methods=["GET"])
def get_progress():
    return jsonify(progress)


@app.route("/tables", methods=["GET"])
def list_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
    )
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([table[0] for table in tables])


@app.route("/table/delete/<table_name>", methods=["DELETE"])
def delete_table(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if not table_name or table_name.strip() == "":
            return jsonify({"error": "无效的表名"}), 400
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        return jsonify({"message": f"表 {table_name} 已成功删除。"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.route("/table/<table_name>", methods=["GET"])
def get_table_data(table_name):
    conn = get_db_connection()
    query = f"SELECT * FROM {table_name} LIMIT 10"
    df = pd.read_sql(query, conn)
    conn.close()
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/contacts/<databaseName>", methods=["GET"])
def get_contacts(databaseName):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT chat_contact FROM {databaseName}")
    contacts = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([contact[0] for contact in contacts])


@app.route("/api/getChatDates/<contact>", methods=["GET"])
def get_dates(contact):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT time::date AS date FROM messages WHERE chat_contact = %s ORDER BY date ASC",
        (contact,),
    )
    dates = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([date[0] for date in dates])


@app.route("/api/dates", methods=["POST"])
def receive_dates():
    data = request.get_json()
    start_date = data.get("startDate")
    end_date = data.get("endDate")

    # Implement your logic here (e.g., save dates to a database)
    print(f"Received dates: Start - {start_date}, End - {end_date}")

    # Send a response back to the client
    return jsonify({"message": "Dates received successfully"}), 200


@app.route("/api/countChatDates", methods=["GET"])
def count_chat_dates():
    data = request.args
    start_date = datetime.fromisoformat(
        data.get("start_date").replace("Z", "+00:00")
    ).date()
    end_date = datetime.fromisoformat(
        data.get("end_date").replace("Z", "+00:00")
    ).date()
    start_date_str = start_date.strftime("%Y-%m-%d")
    print("START", start_date_str)
    end_date_str = end_date.strftime("%Y-%m-%d")
    print("END", end_date_str)
    db_name = data.get("db_name")
    print("DB", db_name)
    chat_contact = data.get("contact_name")
    print("CONTACT", chat_contact)

    query1 = f"""
        SELECT 
            DATE(time) AS chat_date, 
            COUNT(*) AS chat_count
        FROM 
            {db_name}
        WHERE 
            DATE(time) BETWEEN %s AND %s
            AND chat_contact = %s
        GROUP BY 
            chat_date
        ORDER BY 
            chat_date;
    """
    query2 = f""" 
        SELECT 
            DATE(time) AS chat_date, 
            COUNT(*) AS chat_count
        FROM 
            {db_name}
        WHERE 
            DATE(time) BETWEEN %s AND %s
            AND chat_contact = %s
            AND split_part(sender, ' ', 1) = %s
        GROUP BY 
            chat_date
        ORDER BY 
            chat_date;
    """
    query3 = f""" 
        SELECT 
            DATE(time) AS chat_date, 
            COUNT(*) AS chat_count
        FROM 
            {db_name}
        WHERE 
            DATE(time) BETWEEN %s AND %s
            AND chat_contact = %s
            AND split_part(sender, ' ', 1) != %s
        GROUP BY 
            chat_date
        ORDER BY 
            chat_date;
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query1, (start_date_str, end_date_str, chat_contact))
        chat_num_each_day_both = cursor.fetchall()
        cursor.execute(query2, (start_date_str, end_date_str, chat_contact, chat_contact))
        chat_num_each_day_from_contact = cursor.fetchall()
        cursor.execute(query3, (start_date_str, end_date_str, chat_contact, chat_contact))
        chat_num_each_day_from_me = cursor.fetchall()

        print(chat_num_each_day_both)
        max_value = max(row[1] for row in chat_num_each_day_both) if chat_num_each_day_both else 1

        def normalize_chat_counts(chat_data, max_value):
            return [(row[0], row[1] / max_value) for row in chat_data]

        chat_num_each_day_both_normalized = normalize_chat_counts(
            chat_num_each_day_both, max_value
        )
        chat_num_each_day_from_contact_normalized = normalize_chat_counts(
            chat_num_each_day_from_contact, max_value
        )
        chat_num_each_day_from_me_normalized = normalize_chat_counts(
            chat_num_each_day_from_me, max_value
        )

        generate_calendar(
            chat_num_each_day_both_normalized, output_name="calendar_both.png"
        )
        generate_calendar(
            chat_num_each_day_from_contact_normalized,
            output_name="calendar_from_contact.png",
        )
        generate_calendar(
            chat_num_each_day_from_me_normalized, output_name="calendar_from_me.png"
        )

        return jsonify(
            {
                "both": chat_num_each_day_both,
                "from_contact": chat_num_each_day_from_contact,
                "from_me": chat_num_each_day_from_me,
                "images": {
                    "both": "http://127.0.0.1:5000/static/calendar_both.png",
                    "from_contact": "http://127.0.0.1:5000/static/calendar_from_contact.png",
                    "from_me": "http://127.0.0.1:5000/static/calendar_from_me.png",
                }
            }
        ), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print(chat_num_each_day_from_me_normalized)

@app.route("/static/<path:path>")
def send_file(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run(debug=True)
