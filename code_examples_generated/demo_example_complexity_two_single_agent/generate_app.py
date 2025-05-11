# filename: generate_app.py

# This script generates a full-stack web application using Flask, Flask-SocketIO, and SQLite.
# It creates the necessary files: index.html, style.css, script.js, and app.py.
# Dependencies: Flask, Flask-Cors, Flask-SocketIO
# To run the application:
# 1. Install dependencies: pip install Flask Flask-Cors Flask-SocketIO
# 2. Run the application: python app.py

def create_files():
    # HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>User Management</title>
        <link rel="stylesheet" href="style.css">
        <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
        <script src="script.js" defer></script>
    </head>
    <body>
        <h1>User Management</h1>
        <form id="userForm">
            <input type="hidden" id="userId">
            <label for="name">Name:</label>
            <input type="text" id="name" required>
            <label for="age">Age:</label>
            <input type="number" id="age" min="0" required>
            <label for="balance">Balance:</label>
            <input type="number" id="balance" min="0" required>
            <button type="button" id="createUser">Create User</button>
            <button type="button" id="updateUser" style="display:none;">Update User</button>
            <button type="button" id="clearForm">Clear Form</button>
        </form>
        <button id="loadUsers">Load Users</button>
        <div id="status"></div>
        <ul id="userList"></ul>
    </body>
    </html>
    """

    # CSS content
    css_content = """
    body {
        font-family: Arial, sans-serif;
        margin: 20px;
    }
    form {
        margin-bottom: 20px;
    }
    label {
        display: block;
        margin-top: 10px;
    }
    input {
        margin-bottom: 10px;
    }
    button {
        margin-right: 10px;
    }
    #userList {
        list-style-type: none;
        padding: 0;
    }
    #userList li {
        padding: 10px;
        border-bottom: 1px solid #ccc;
    }
    """

    # JavaScript content
    js_content = """
    const socket = io('http://127.0.0.1:5000');

    document.getElementById('createUser').addEventListener('click', createUser);
    document.getElementById('updateUser').addEventListener('click', updateUser);
    document.getElementById('clearForm').addEventListener('click', clearForm);
    document.getElementById('loadUsers').addEventListener('click', loadUsers);

    socket.on('user_update', (data) => {
        displayUsers(data.users);
    });

    function createUser() {
        const name = document.getElementById('name').value;
        const age = document.getElementById('age').value;
        const balance = document.getElementById('balance').value;
        fetch('http://127.0.0.1:5000/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, age, balance })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('status').innerText = data.error;
            } else {
                clearForm();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function updateUser() {
        const id = document.getElementById('userId').value;
        const name = document.getElementById('name').value;
        const age = document.getElementById('age').value;
        const balance = document.getElementById('balance').value;
        fetch(`http://127.0.0.1:5000/users/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, age, balance })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('status').innerText = data.error;
            } else {
                clearForm();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function loadUsers() {
        fetch('http://127.0.0.1:5000/users')
        .then(response => response.json())
        .then(data => displayUsers(data))
        .catch(error => console.error('Error:', error));
    }

    function displayUsers(users) {
        const userList = document.getElementById('userList');
        userList.innerHTML = '';
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = `Name: ${user.name}, Age: ${user.age}, Balance: ${user.balance}`;
            userList.appendChild(li);
        });
    }

    function clearForm() {
        document.getElementById('userId').value = '';
        document.getElementById('name').value = '';
        document.getElementById('age').value = '';
        document.getElementById('balance').value = '';
        document.getElementById('updateUser').style.display = 'none';
        document.getElementById('createUser').style.display = 'inline';
    }
    """

    # Python (Flask) content
    python_content = """
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
    """

    # Write files
    with open('index.html', 'w') as f:
        f.write(html_content)
    with open('style.css', 'w') as f:
        f.write(css_content)
    with open('script.js', 'w') as f:
        f.write(js_content)
    with open('app.py', 'w') as f:
        f.write(python_content)

if __name__ == '__main__':
    create_files()
    print("Files generated: index.html, style.css, script.js, app.py")
    print("To run the application, install dependencies with 'pip install Flask Flask-Cors Flask-SocketIO' and execute 'python app.py'.")