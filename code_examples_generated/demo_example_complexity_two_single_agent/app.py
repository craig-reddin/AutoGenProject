
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

    @app.route('/')
    def index():
        return send_from_directory('', 'index.html')

    @app.route('/users', methods=['GET', 'POST'])
    def users():
        if request.method == 'GET':
            return jsonify(_get_all_users_as_list())
        elif request.method == 'POST':
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
                socketio.emit('user_update', {'users': _get_all_users_as_list()})
                return jsonify({'id': cursor.lastrowid, 'name': name, 'age': age, 'balance': balance}), 201

    @app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
    def user(user_id):
        if request.method == 'GET':
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                if user:
                    return jsonify({'id': user[0], 'name': user[1], 'age': user[2], 'balance': user[3]})
                return jsonify({'error': 'User not found'}), 404
        elif request.method == 'PUT':
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
                socketio.emit('user_update', {'users': _get_all_users_as_list()})
                return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance})
        elif request.method == 'DELETE':
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
                socketio.emit('user_update', {'users': _get_all_users_as_list()})
                return jsonify({'message': 'User deleted'})

    def _get_all_users_as_list():
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
            return [{'id': user[0], 'name': user[1], 'age': user[2], 'balance': user[3]} for user in users]

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    if __name__ == '__main__':
        init_db()
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    