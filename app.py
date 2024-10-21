from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable CORS to allow frontend to access the API
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Netlify

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('tracker.db')
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

@app.route('/activities', methods=['POST'])
def add_activity():
    data = request.json
    hour = data.get('hour')
    activity = data.get('activity')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activities (timestamp, hour, activity)
        VALUES (?, ?, ?)
    ''', (timestamp, hour, activity))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Activity added successfully'}), 201

@app.route('/activities', methods=['GET'])
def get_activities():
    conn = sqlite3.connect('tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, hour, activity FROM activities ORDER BY timestamp DESC')
    activities = cursor.fetchall()
    conn.close()

    result = [{'timestamp': t, 'hour': h, 'activity': a} for (t, h, a) in activities]
    return jsonify(result), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
