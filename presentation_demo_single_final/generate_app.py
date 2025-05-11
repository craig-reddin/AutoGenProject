# filename: generate_app.py

"""
This script generates a full-stack web application using Flask, Flask-SocketIO, and SQLite.
It creates the necessary files: index.html, style.css, script.js, and app.py.
Dependencies: Flask, Flask-Cors, Flask-SocketIO
To install dependencies, run: pip install Flask Flask-Cors Flask-SocketIO
To run the application, use: python app.py
"""

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
        <script defer src="script.js"></script>
    </head>
    <body>
        <h1>User Management</h1>
        <form id="userForm">
            <input type="hidden" id="userId">
            <input type="text" id="name" placeholder="Name" required>
            <input type="number" id="age" placeholder="Age" min="0" required>
            <input type="number" id="balance" placeholder="Balance" min="0" required>
            <button type="button" id="createUser">Create User</button>
            <button type="button" id="updateUser" style="display:none;">Update User</button>
            <button type="button" id="clearForm">Clear Form</button>
            <button type="button" id="loadUsers">Load Users</button>
        </form>
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
        padding: 0;
    }
    form {
        display: flex;
        flex-direction: column;
        max-width: 300px;
    }
    input {
        margin-bottom: 10px;
        padding: 8px;
        font-size: 16px;
    }
    button {
        padding: 10px;
        font-size: 16px;
        margin-bottom: 10px;
        cursor: pointer;
    }
    ul {
        list-style-type: none;
        padding: 0;
    }
    li {
        padding: 8px;
        border: 1px solid #ccc;
        margin-bottom: 5px;
    }
    """

    # JavaScript content
    js_content = """
    const socket = io('http://127.0.0.1:5000');

    document.addEventListener('DOMContentLoaded', () => {
        const userForm = document.getElementById('userForm');
        const statusDiv = document.getElementById('status');
        const userList = document.getElementById('userList');

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
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, age, balance })
            })
            .then(response => response.json())
            .then(data => {
                statusDiv.textContent = 'User created successfully.';
                clearForm();
            })
            .catch(error => {
                statusDiv.textContent = 'Error creating user: ' + error;
            });
        }

        function updateUser() {
            const id = document.getElementById('userId').value;
            const name = document.getElementById('name').value;
            const age = document.getElementById('age').value;
            const balance = document.getElementById('balance').value;
            fetch(`http://127.0.0.1:5000/users/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, age, balance })
            })
            .then(response => response.json())
            .then(data => {
                statusDiv.textContent = 'User updated successfully.';
                clearForm();
            })
            .catch(error => {
                statusDiv.textContent = 'Error updating user: ' + error;
            });
        }

        function clearForm() {
            userForm.reset();
            document.getElementById('userId').value = '';
            document.getElementById('updateUser').style.display = 'none';
            document.getElementById('createUser').style.display = 'inline';
        }

        function loadUsers() {
            fetch('http://127.0.0.1:5000/users')
            .then(response => response.json())
            .then(data => {
                displayUsers(data.users);
            })
            .catch(error => {
                statusDiv.textContent = 'Error loading users: ' + error;
            });
        }

        function displayUsers(users) {
            userList.innerHTML = '';
            users.forEach(user => {
                const li = document.createElement('li');
                li.textContent = `Name: ${user.name}, Age: ${user.age}, Balance: ${user.balance}`;
                li.addEventListener('click', () => {
                    document.getElementById('userId').value = user.id;
                    document.getElementById('name').value = user.name;
                    document.getElementById('age').value = user.age;
                    document.getElementById('balance').value = user.balance;
                    document.getElementById('updateUser').style.display = 'inline';
                    document.getElementById('createUser').style.display = 'none';
                });
                userList.appendChild(li);
            });
        }
    });
    """

    # Python (Flask) content
    python_content = """
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
    """

    # Write the files
    with open('index.html', 'w') as f:
        f.write(html_content)

    with open('style.css', 'w') as f:
        f.write(css_content)

    with open('script.js', 'w') as f:
        f.write(js_content)

    with open('app.py', 'w') as f:
        f.write(python_content)

if __name__ == "__main__":
    create_files()
    print("Files generated successfully. Run the application with: python app.py")