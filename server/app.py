from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import psycopg2 as pg
from datetime import datetime
from tqdm import tqdm
import threading
import pandas as pd
from utils.generate_calendar import generate_calendar
from utils.generate_wordcloud import generate_wordcloud
from utils.generate_sentiment import analyze_sentiment_and_generate_tsne
from utils.generate_social_graph import generate_social_graph
from psycopg2 import sql
from utils.generate_chatnum_piechart import generate_pie_chart
from utils.generate_radarchart import generate_radar_chart

app = Flask(__name__)
CORS(app)

TEMP_JSON_PATH = "./uploads/result.json"

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
        Drop TABLE IF EXISTS {table_name};
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
            return jsonify({"error": "Invalid table name."}), 400
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        return jsonify({"message": f"Table {table_name} has been successfully deleted."}), 200
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


@app.route("/api/getChatDates/<databaseName>/<contact>", methods=["GET"])
def get_dates(databaseName, contact):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL(
        "SELECT DISTINCT time::date AS date FROM {} WHERE chat_contact = %s ORDER BY date ASC"
    ).format(sql.Identifier(databaseName))
    cursor.execute(query, (contact,))
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

        max_value = max(row[1] for row in chat_num_each_day_both) if chat_num_each_day_both else 1

        def normalize_chat_counts(chat_data, max_value):
            return [(row[0], row[1] / max_value) for row in chat_data] if chat_data else []

        # Normalize each dataset
        chat_num_each_day_both_normalized = normalize_chat_counts(chat_num_each_day_both, max_value)
        chat_num_each_day_from_contact_normalized = normalize_chat_counts(chat_num_each_day_from_contact, max_value)
        chat_num_each_day_from_me_normalized = normalize_chat_counts(chat_num_each_day_from_me, max_value)

        # Generate calendar only if the data is not empty
        if chat_num_each_day_both_normalized:
            generate_calendar(chat_num_each_day_both_normalized, output_name="calendar_both.png")
        else:
            print("No data for both chats. Skipping calendar generation.")

        # if chat_num_each_day_from_contact_normalized:
        #     generate_calendar(chat_num_each_day_from_contact_normalized, output_name="calendar_from_contact.png")
        # else:
        #     print("No data from contact. Skipping calendar generation.")

        # if chat_num_each_day_from_me_normalized:
        #     generate_calendar(chat_num_each_day_from_me_normalized, output_name="calendar_from_me.png")
        # else:
        #     print("No data from me. Skipping calendar generation.")

        return jsonify(
            {
                "both": chat_num_each_day_both,
                "from_contact": chat_num_each_day_from_contact,
                "from_me": chat_num_each_day_from_me,
                "images": {
                    "both": "http://127.0.0.1:5000/static/calendar_both.png",
                    # "from_contact": "http://127.0.0.1:5000/static/calendar_from_contact.png",
                    # "from_me": "http://127.0.0.1:5000/static/calendar_from_me.png",
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

@app.route("/api/wordcloud", methods=["GET"])
def generate_word_cloud():
    data = request.args
    start_date = datetime.fromisoformat(
        data.get("start_date").replace("Z", "+00:00")
    ).date()
    end_date = datetime.fromisoformat(
        data.get("end_date").replace("Z", "+00:00")
    ).date()
    db_name = data.get("db_name")
    chat_contact = data.get("contact_name")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"""
            SELECT text
            FROM {db_name}
            WHERE DATE(time) BETWEEN %s AND %s
              AND chat_contact = %s
        """
        cursor.execute(query, (start_date, end_date, chat_contact))
        texts = cursor.fetchall()
        text_data = [row[0] for row in texts if row[0]]

        if not text_data:
            return jsonify({"error": "No text data found for the specified criteria."}), 404

        # Generate word cloud
        output_name = f"wordcloud_{chat_contact}.png"
        output_path = generate_wordcloud(text_data, output_name=output_name)

        # Return the image URL
        image_url = f"http://127.0.0.1:5000/static/{output_name}"
        return jsonify({"image": image_url}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/api/sentiment", methods=["GET"])
def perform_sentiment_analysis():
    data = request.args
    start_date = datetime.fromisoformat(data.get("start_date").replace("Z", "+00:00")).date()
    end_date = datetime.fromisoformat(data.get("end_date").replace("Z", "+00:00")).date()
    db_name = data.get("db_name")
    chat_contact = data.get("contact_name")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"""
            SELECT text
            FROM {db_name}
            WHERE DATE(time) BETWEEN %s AND %s
              AND chat_contact = %s
        """
        cursor.execute(query, (start_date, end_date, chat_contact))
        texts = cursor.fetchall()
        text_data = [row[0] for row in texts if row[0]]

        if not text_data:
            return jsonify({"error": "No text data found for the specified criteria."}), 404

        # Call the sentiment analysis and t-SNE function
        output_path = analyze_sentiment_and_generate_tsne(text_data)

        # Return the image URL
        image_url = f"http://127.0.0.1:5000/{output_path}"
        return jsonify({"image": image_url}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            

@app.route("/api/radar_chat_time", methods=["GET"])
def generate_radar_chat_time():
    data = request.args
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    db_name = data.get("db_name")
    chat_contact = data.get("contact_name")

    # Validate required parameters
    if not all([start_date_str, end_date_str, db_name, chat_contact]):
        return jsonify({"error": "Missing required query parameters."}), 400

    try:
        # Parse dates
        start_date = datetime.fromisoformat(
            start_date_str.replace("Z", "+00:00")
        ).date()
        end_date = datetime.fromisoformat(
            end_date_str.replace("Z", "+00:00")
        ).date()
    except ValueError as ve:
        return jsonify({"error": f"Invalid date format: {ve}"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to count messages by hour
        query = f"""
            SELECT EXTRACT(HOUR FROM time) as hour, COUNT(*) as message_count
            FROM {db_name}
            WHERE DATE(time) BETWEEN %s AND %s
              AND chat_contact = %s
            GROUP BY hour
            ORDER BY hour
        """
        cursor.execute(query, (start_date, end_date, chat_contact))
        results = cursor.fetchall()

        if not results:
            return jsonify({"error": "No chat data found for the specified criteria."}), 404

        # Create a list of message counts by hour (0 to 23)
        hourly_counts = [0] * 24  # Initialize counts for all hours
        for hour, count in results:
            hourly_counts[int(hour)] = count

        # Generate radar chart
        timestamp = int(datetime.now().timestamp())
        output_name = f"radar_chart.png"
        output_path = generate_radar_chart(hourly_counts, output_name=output_name)

        # Construct the image URL
        image_url = f"http://127.0.0.1:5000/static/{output_name}"

        return jsonify({"image": image_url}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            

@app.route("/api/pie_chart_chat_numbers", methods=["GET"])
def generate_pie_chart_chat_numbers():
    data = request.args
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    db_name = data.get("db_name")
    chat_contact = data.get("contact_name")

    # Validate required parameters
    if not all([start_date_str, end_date_str, db_name, chat_contact]):
        return jsonify({"error": "Missing required query parameters."}), 400

    try:
        # Parse dates
        start_date = datetime.fromisoformat(
            start_date_str.replace("Z", "+00:00")
        ).date()
        end_date = datetime.fromisoformat(
            end_date_str.replace("Z", "+00:00")
        ).date()
    except ValueError as ve:
        return jsonify({"error": f"Invalid date format: {ve}"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to count messages per sender for a specific chat contact and date range
        query = f"""
            SELECT sender, COUNT(*) as message_count
            FROM {db_name}
            WHERE DATE(time) BETWEEN %s AND %s
              AND chat_contact = %s
            GROUP BY sender
            ORDER BY message_count DESC
        """
        cursor.execute(query, (start_date, end_date, chat_contact))
        results = cursor.fetchall()

        if not results:
            return jsonify({"error": "No chat data found for the specified criteria."}), 404

        # Create a dictionary of message counts per sender
        chat_counts = {row[0]: row[1] for row in results}

        if not chat_counts:
            return jsonify({"error": "No valid user data found for the specified criteria."}), 404

        # Generate pie chart
        timestamp = int(datetime.now().timestamp())
        output_name = f"pie_chart.png"
        output_path = generate_pie_chart(chat_counts, output_name=output_name)

        # Construct the image URL
        image_url = f"http://127.0.0.1:5000/static/{output_name}"

        return jsonify({"image": image_url}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            

@app.route("/api/social_graph", methods=["GET"])
def create_social_network_graph():
    data = request.args
    start_date = datetime.fromisoformat(data.get("start_date").replace("Z", "+00:00")).date()
    end_date = datetime.fromisoformat(data.get("end_date").replace("Z", "+00:00")).date()
    db_name = data.get("db_name")
    chat_contact = data.get("contact_name")
    min_edge_weight = int(data.get("min_edge_weight", 3))  # Default to 3
    top_n_nodes = int(data.get("top_n_nodes", 100))        # Default to 100

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"""
            SELECT sender
            FROM {db_name}
            WHERE DATE(time) BETWEEN %s AND %s
              AND chat_contact = %s
              AND sender IS NOT NULL
            ORDER BY time ASC
        """
        cursor.execute(query, (start_date, end_date, chat_contact))
        messages = [{"sender": row[0]} for row in cursor.fetchall()]

        if not messages:
            return jsonify({"error": "No messages found for the specified criteria."}), 404

        # Generate the social network graph
        output_path = generate_social_graph(
            messages, 
            min_edge_weight=min_edge_weight, 
            top_n_nodes=top_n_nodes
        )

        # Return the graph image URL
        image_url = f"http://127.0.0.1:5000/{output_path}"
        return jsonify({"image": image_url}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/static/<path:path>")
def send_file(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run(debug=True)
