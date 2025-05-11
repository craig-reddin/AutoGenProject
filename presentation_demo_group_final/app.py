
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlite3
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

DB_NAME = 'users.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                balance REAL NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

@app.route('/users', methods=['GET', 'POST'])
def manage_users():
    if request.method == 'GET':
        search_query = request.args.get('q', '')
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            if search_query:
                cursor.execute('SELECT * FROM users WHERE name LIKE ?', ('%' + search_query + '%',))
            else:
                cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
            return jsonify([{'id': row[0], 'name': row[1], 'age': row[2], 'balance': row[3]} for row in users])

    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        age = data.get('age')
        balance = data.get('balance')
        if not all([name, age, balance]):
            return jsonify({'message': 'Invalid input'}), 400
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (name, age, balance) VALUES (?, ?, ?)', (name, age, balance))
            conn.commit()
            new_user_id = cursor.lastrowid
            socketio.emit('user_update')
            return jsonify({'id': new_user_id, 'name': name, 'age': age, 'balance': balance}), 201

@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_user(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if request.method == 'GET':
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            if user:
                return jsonify({'id': user[0], 'name': user[1], 'age': user[2], 'balance': user[3]})
            return jsonify({'message': 'User not found'}), 404

        if request.method == 'PUT':
            data = request.json
            name = data.get('name')
            age = data.get('age')
            balance = data.get('balance')
            if not all([name, age, balance]):
                return jsonify({'message': 'Invalid input'}), 400
            cursor.execute('UPDATE users SET name = ?, age = ?, balance = ? WHERE id = ?', (name, age, balance, user_id))
            conn.commit()
            socketio.emit('user_update')
            return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance})

        if request.method == 'DELETE':
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            socketio.emit('user_update')
            return jsonify({'message': 'User deleted'})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
