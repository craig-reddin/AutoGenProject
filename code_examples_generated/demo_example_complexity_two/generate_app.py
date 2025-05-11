# filename: generate_app.py

# This script generates a full-stack web application using Flask, Flask-SocketIO, and SQLite.
# It creates the necessary files: index.html, style.css, script.js, and app.py.
# Dependencies: Flask, Flask-Cors, Flask-SocketIO
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
    <h1>User Management</h1>
    <form id="userForm">
        <input type="hidden" id="userId">
        <label for="name">Name:</label>
        <input type="text" id="name" required>
        <label for="age">Age:</label>
        <input type="number" id="age" min="0" required>
        <label for="balance">Balance:</label>
        <input type="number" id="balance" min="0" required>
        <button type="submit" id="createUser">Create User</button>
        <button type="button" id="updateUser" style="display:none;">Update User</button>
        <button type="button" id="clearForm">Clear Form</button>
    </form>
    <button id="loadUsers">Load Users</button>
    <input type="text" id="searchQuery" placeholder="Search...">
    <button id="searchButton">Search</button>
    <div id="statusMessage"></div>
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
    display: flex;
    flex-direction: column;
    max-width: 300px;
}
label {
    margin-top: 10px;
}
button {
    margin-top: 10px;
}
#userList {
    margin-top: 20px;
    list-style-type: none;
    padding: 0;
}
#userList li {
    padding: 10px;
    border: 1px solid #ccc;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
}
"""

# JavaScript content
js_content = """
const socket = io('http://127.0.0.1:5000');

document.addEventListener('DOMContentLoaded', () => {
    const userForm = document.getElementById('userForm');
    const createUserButton = document.getElementById('createUser');
    const updateUserButton = document.getElementById('updateUser');
    const clearFormButton = document.getElementById('clearForm');
    const loadUsersButton = document.getElementById('loadUsers');
    const searchButton = document.getElementById('searchButton');
    const userList = document.getElementById('userList');
    const statusMessage = document.getElementById('statusMessage');

    const displayUsers = (users) => {
        userList.innerHTML = '';
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = `Name: ${user.name}, Age: ${user.age}, Balance: ${user.balance}`;
            const editButton = document.createElement('button');
            editButton.textContent = 'Edit';
            editButton.onclick = () => populateForm(user);
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.onclick = () => deleteUser(user.id);
            li.appendChild(editButton);
            li.appendChild(deleteButton);
            userList.appendChild(li);
        });
    };

    const populateForm = (user) => {
        document.getElementById('userId').value = user.id;
        document.getElementById('name').value = user.name;
        document.getElementById('age').value = user.age;
        document.getElementById('balance').value = user.balance;
        createUserButton.style.display = 'none';
        updateUserButton.style.display = 'inline';
    };

    const clearForm = () => {
        document.getElementById('userId').value = '';
        document.getElementById('name').value = '';
        document.getElementById('age').value = '';
        document.getElementById('balance').value = '';
        createUserButton.style.display = 'inline';
        updateUserButton.style.display = 'none';
    };

    const showMessage = (message) => {
        statusMessage.textContent = message;
        setTimeout(() => statusMessage.textContent = '', 3000);
    };

    const fetchUsers = (query = '') => {
        fetch(`http://127.0.0.1:5000/users?search=${query}`)
            .then(response => response.json())
            .then(data => displayUsers(data))
            .catch(error => showMessage('Error loading users'));
    };

    const createUser = (user) => {
        fetch('http://127.0.0.1:5000/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(user)
        })
        .then(response => response.json())
        .then(data => {
            showMessage('User created successfully');
            clearForm();
        })
        .catch(error => showMessage('Error creating user'));
    };

    const updateUser = (user) => {
        fetch(`http://127.0.0.1:5000/users/${user.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(user)
        })
        .then(response => response.json())
        .then(data => {
            showMessage('User updated successfully');
            clearForm();
        })
        .catch(error => showMessage('Error updating user'));
    };

    const deleteUser = (id) => {
        fetch(`http://127.0.0.1:5000/users/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => showMessage('User deleted successfully'))
        .catch(error => showMessage('Error deleting user'));
    };

    userForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const user = {
            id: document.getElementById('userId').value,
            name: document.getElementById('name').value,
            age: document.getElementById('age').value,
            balance: document.getElementById('balance').value
        };
        if (user.id) {
            updateUser(user);
        } else {
            createUser(user);
        }
    });

    clearFormButton.addEventListener('click', clearForm);
    loadUsersButton.addEventListener('click', () => fetchUsers());
    searchButton.addEventListener('click', () => {
        const query = document.getElementById('searchQuery').value;
        fetchUsers(query);
    });

    socket.on('user_update', (data) => {
        displayUsers(data.users);
    });

    fetchUsers();
});
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

print("Files generated: index.html, style.css, script.js, app.py")
print("To run the application, execute: python app.py")