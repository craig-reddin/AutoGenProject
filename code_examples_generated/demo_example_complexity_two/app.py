
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlite3

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

def _get_all_users_as_list():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = [{'id': row[0], 'name': row[1], 'age': row[2], 'balance': row[3]} for row in cursor.fetchall()]
    return users

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/users', methods=['GET'])
def get_users():
    search_query = request.args.get('search', '')
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if search_query:
            cursor.execute('SELECT * FROM users WHERE name LIKE ?', ('%' + search_query + '%',))
        else:
            cursor.execute('SELECT * FROM users')
        users = [{'id': row[0], 'name': row[1], 'age': row[2], 'balance': row[3]} for row in cursor.fetchall()]
    return jsonify(users)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, age, balance) VALUES (?, ?, ?)', (data['name'], data['age'], data['balance']))
        conn.commit()
    socketio.emit('user_update', {'users': _get_all_users_as_list()})
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET name = ?, age = ?, balance = ? WHERE id = ?', (data['name'], data['age'], data['balance'], user_id))
        conn.commit()
    socketio.emit('user_update', {'users': _get_all_users_as_list()})
    return jsonify({'message': 'User updated successfully'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
    socketio.emit('user_update', {'users': _get_all_users_as_list()})
    return jsonify({'message': 'User deleted successfully'})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
