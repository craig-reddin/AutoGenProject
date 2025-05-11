from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlite3

DB_NAME = 'users.db'

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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

@app.route('/users', methods=['GET'])
def get_users():
    search = request.args.get('search', '')
    query = 'SELECT * FROM users WHERE name LIKE ?'
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, ('%' + search + '%',))
        users = cursor.fetchall()
    return jsonify([{'id': user[0], 'name': user[1], 'age': user[2], 'balance': user[3]} for user in users])

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    balance = data.get('balance')
    if not name or age is None or balance is None:
        return jsonify({'error': 'Invalid input'}), 400
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, age, balance) VALUES (?, ?, ?)', (name, age, balance))
        conn.commit()
        user_id = cursor.lastrowid
    socketio.emit('user_update', get_all_users_as_list())
    return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance}), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
    if user:
        return jsonify({'id': user[0], 'name': user[1], 'age': user[2], 'balance': user[3]})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    name = data.get('name')
    age = data.get('age')
    balance = data.get('balance')
    if not name or age is None or balance is None:
        return jsonify({'error': 'Invalid input'}), 400
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET name = ?, age = ?, balance = ? WHERE id = ?', (name, age, balance, user_id))
        conn.commit()
    socketio.emit('user_update', get_all_users_as_list())
    return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
    socketio.emit('user_update', get_all_users_as_list())
    return jsonify({'result': 'success'})

def get_all_users_as_list():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
    return [{'id': user[0], 'name': user[1], 'age': user[2], 'balance': user[3]} for user in users]

@socketio.on('connect')
def on_connect():
    emit('user_update', get_all_users_as_list())

@socketio.on('disconnect')
def on_disconnect():
    pass

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
