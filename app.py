import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable CORS to allow frontend to access the API
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Netlify

# Define the absolute path to the SQLite database
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracker.db')

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return results as dictionaries
    return conn

def init_db():
    """Create the 'activities' table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            hour TEXT NOT NULL,
            activity TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Ensure the database is initialized on every startup
@app.before_first_request
def initialize():
    init_db()

@app.route('/activities', methods=['POST'])
def add_activity():
    try:
        data = request.json
        hour = data.get('hour')
        activity = data.get('activity')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activities (timestamp, hour, activity)
            VALUES (?, ?, ?)
        ''', (timestamp, hour, activity))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Activity added successfully'}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to add activity'}), 500

@app.route('/activities', methods=['GET'])
def get_activities():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, hour, activity FROM activities ORDER BY timestamp DESC')
        activities = cursor.fetchall()
        conn.close()

        result = [{'timestamp': row['timestamp'], 'hour': row['hour'], 'activity': row['activity']}
                  for row in activities]
        return jsonify(result), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to fetch activities'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
