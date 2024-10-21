from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE = 'tracker.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            start_hour TEXT NOT NULL,
            end_hour TEXT NOT NULL,
            activity TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/activities', methods=['POST'])
def add_activity():
    data = request.json
    start_hour = data.get('startHour')
    end_hour = data.get('endHour')
    activity = data.get('activity')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activities (timestamp, start_hour, end_hour, activity)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, start_hour, end_hour, activity))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Activity added successfully'}), 201

@app.route('/activities', methods=['GET'])
def get_activities():
    date = request.args.get('date')
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute('SELECT * FROM activities WHERE DATE(timestamp) = ?', (date,))
    else:
        cursor.execute('SELECT * FROM activities ORDER BY timestamp DESC')
    activities = cursor.fetchall()
    conn.close()

    result = [{'id': row['id'], 'timestamp': row['timestamp'], 'startHour': row['start_hour'],
               'endHour': row['end_hour'], 'activity': row['activity']} for row in activities]
    return jsonify(result), 200

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM activities WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Activity deleted successfully'}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
