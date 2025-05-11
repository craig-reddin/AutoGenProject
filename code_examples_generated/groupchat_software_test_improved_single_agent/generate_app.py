# filename: generate_app.py

# This script generates a full-stack web application using Flask, Flask-SocketIO, and SQLite.
# It creates the necessary files: index.html, style.css, script.js, and app.py.
# Required dependencies: Flask, Flask-Cors, Flask-SocketIO
# To install dependencies, run: pip install Flask Flask-Cors Flask-SocketIO
# To run the application, execute: python app.py

import os

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
    <div id="app">
        <h1>User Management</h1>
        <form id="user-form">
            <input type="hidden" id="user-id">
            <label for="name">Name:</label>
            <input type="text" id="name" required>
            <label for="age">Age:</label>
            <input type="number" id="age" min="0" required>
            <label for="balance">Balance:</label>
            <input type="number" id="balance" min="0" required>
            <button type="button" id="create-user">Create User</button>
            <button type="button" id="update-user" style="display:none;">Update User</button>
            <button type="button" id="clear-form">Clear Form</button>
            <button type="button" id="load-users">Load Users</button>
        </form>
        <div id="status"></div>
        <ul id="user-list"></ul>
    </div>
</body>
</html>
"""

# CSS content
css_content = """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f0f0f0;
}

#app {
    width: 80%;
    max-width: 600px;
    background-color: #fff;
    padding: 20px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
}

form {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

button {
    padding: 10px;
    background-color: #007bff;
    color: #fff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

#user-list {
    list-style: none;
    padding: 0;
}

#user-list li {
    padding: 10px;
    border-bottom: 1px solid #ddd;
}

#status {
    margin-top: 10px;
    color: red;
}
"""

# JavaScript content
js_content = """
const socket = io('http://127.0.0.1:5000');

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('user-form');
    const createButton = document.getElementById('create-user');
    const updateButton = document.getElementById('update-user');
    const clearButton = document.getElementById('clear-form');
    const loadButton = document.getElementById('load-users');
    const statusDiv = document.getElementById('status');
    const userList = document.getElementById('user-list');

    socket.on('user_update', (data) => {
        displayUsers(data);
    });

    createButton.addEventListener('click', () => {
        const user = getUserFromForm();
        if (user) {
            fetch('http://127.0.0.1:5000/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    statusDiv.textContent = data.error;
                } else {
                    statusDiv.textContent = 'User created successfully';
                    clearForm();
                }
            })
            .catch(error => {
                statusDiv.textContent = 'Error creating user';
            });
        }
    });

    updateButton.addEventListener('click', () => {
        const user = getUserFromForm();
        const userId = document.getElementById('user-id').value;
        if (user && userId) {
            fetch(`http://127.0.0.1:5000/users/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    statusDiv.textContent = data.error;
                } else {
                    statusDiv.textContent = 'User updated successfully';
                    clearForm();
                }
            })
            .catch(error => {
                statusDiv.textContent = 'Error updating user';
            });
        }
    });

    clearButton.addEventListener('click', () => {
        clearForm();
    });

    loadButton.addEventListener('click', () => {
        loadUsers();
    });

    function loadUsers() {
        fetch('http://127.0.0.1:5000/users')
            .then(response => response.json())
            .then(data => {
                displayUsers(data);
            })
            .catch(error => {
                statusDiv.textContent = 'Error loading users';
            });
    }

    function displayUsers(users) {
        userList.innerHTML = '';
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = `Name: ${user.name}, Age: ${user.age}, Balance: ${user.balance}`;
            li.dataset.id = user.id;
            li.addEventListener('click', () => {
                document.getElementById('name').value = user.name;
                document.getElementById('age').value = user.age;
                document.getElementById('balance').value = user.balance;
                document.getElementById('user-id').value = user.id;
                createButton.style.display = 'none';
                updateButton.style.display = 'block';
            });
            userList.appendChild(li);
        });
    }

    function getUserFromForm() {
        const name = document.getElementById('name').value;
        const age = document.getElementById('age').value;
        const balance = document.getElementById('balance').value;
        if (!name || !age || !balance) {
            statusDiv.textContent = 'All fields are required';
            return null;
        }
        return { name, age, balance };
    }

    function clearForm() {
        form.reset();
        document.getElementById('user-id').value = '';
        createButton.style.display = 'block';
        updateButton.style.display = 'none';
        statusDiv.textContent = '';
    }

    loadUsers();
});
"""

# Python (Flask) content
python_content = """
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
"""

# Write contents to files
with open('index.html', 'w') as f:
    f.write(html_content)

with open('style.css', 'w') as f:
    f.write(css_content)

with open('script.js', 'w') as f:
    f.write(js_content)

with open('app.py', 'w') as f:
    f.write(python_content)

print("Files generated successfully. Run the application using: python app.py")