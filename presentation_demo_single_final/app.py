
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit
    import sqlite3

    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="*")

    DB_NAME = 'users.db'

    def init_db():
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            age INTEGER NOT NULL,
                            balance REAL NOT NULL)''')

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/users', methods=['GET', 'POST'])
    def users():
        if request.method == 'POST':
            data = request.json
            name = data.get('name')
            age = data.get('age')
            balance = data.get('balance')
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO users (name, age, balance) VALUES (?, ?, ?)', (name, age, balance))
                conn.commit()
                user_id = cur.lastrowid
                socketio.emit('user_update', {'users': _get_all_users_as_list()})
                return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance}), 201

        if request.method == 'GET':
            return jsonify({'users': _get_all_users_as_list()})

    @app.route('/users/<int:user_id>', methods=['PUT', 'DELETE'])
    def user(user_id):
        if request.method == 'PUT':
            data = request.json
            name = data.get('name')
            age = data.get('age')
            balance = data.get('balance')
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute('UPDATE users SET name = ?, age = ?, balance = ? WHERE id = ?', (name, age, balance, user_id))
                conn.commit()
                socketio.emit('user_update', {'users': _get_all_users_as_list()})
                return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance})

        if request.method == 'DELETE':
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
                socketio.emit('user_update', {'users': _get_all_users_as_list()})
                return jsonify({'message': 'User deleted'})

    def _get_all_users_as_list():
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name, age, balance FROM users')
            users = cur.fetchall()
            return [{'id': row[0], 'name': row[1], 'age': row[2], 'balance': row[3]} for row in users]

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    if __name__ == '__main__':
        init_db()
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    