
from flask import Flask, jsonify, request, send_from_directory
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
def index():
    return send_from_directory('', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('', 'style.css')

@app.route('/script.js')
def script():
    return send_from_directory('', 'script.js')

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        search = request.args.get('search', '')
        return jsonify(get_all_users(search))
    elif request.method == 'POST':
        user_data = request.json
        if not user_data.get('name') or not isinstance(user_data.get('age'), int) or not isinstance(user_data.get('balance'), (int, float)):
            return jsonify({'error': 'Invalid input'}), 400
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (name, age, balance) VALUES (?, ?, ?)', (user_data['name'], user_data['age'], user_data['balance']))
            conn.commit()
            user_id = cursor.lastrowid
            user = get_user_by_id(user_id)
            socketio.emit('user_update', get_all_users())
            return jsonify(user), 201

@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_detail(user_id):
    if request.method == 'GET':
        user = get_user_by_id(user_id)
        if user:
            return jsonify(user)
        return jsonify({'error': 'User not found'}), 404
    elif request.method == 'PUT':
        user_data = request.json
        if not user_data.get('name') or not isinstance(user_data.get('age'), int) or not isinstance(user_data.get('balance'), (int, float)):
            return jsonify({'error': 'Invalid input'}), 400
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET name = ?, age = ?, balance = ? WHERE id = ?', (user_data['name'], user_data['age'], user_data['balance'], user_id))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'User not found'}), 404
            user = get_user_by_id(user_id)
            socketio.emit('user_update', get_all_users())
            return jsonify(user)
    elif request.method == 'DELETE':
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'User not found'}), 404
            socketio.emit('user_update', get_all_users())
            return jsonify({'message': 'User deleted'})

def get_all_users(search=''):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM users WHERE name LIKE ?'
        cursor.execute(query, (f'%{search}%',))
        users = [{'id': row[0], 'name': row[1], 'age': row[2], 'balance': row[3]} for row in cursor.fetchall()]
        return users

def get_user_by_id(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'age': row[2], 'balance': row[3]}
        return None

@socketio.on('connect')
def handle_connect():
    emit('user_update', get_all_users())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
