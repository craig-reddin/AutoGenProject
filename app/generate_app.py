# filename: generate_app.py

# This script generates a full-stack web application with real-time updates using Flask, Flask-SocketIO, and SQLite.
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
    <script defer src="script.js"></script>
</head>
<body>
    <h1>User Management</h1>
    <div id="status"></div>
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
    <input type="text" id="searchQuery" placeholder="Search...">
    <button id="searchButton">Search</button>
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

#userList li:nth-child(odd) {
    background-color: #f9f9f9;
}
"""

# JavaScript content
js_content = """
const socket = io('http://127.0.0.1:5000');

document.addEventListener('DOMContentLoaded', () => {
    const userForm = document.getElementById('userForm');
    const userIdInput = document.getElementById('userId');
    const nameInput = document.getElementById('name');
    const ageInput = document.getElementById('age');
    const balanceInput = document.getElementById('balance');
    const createUserButton = document.getElementById('createUser');
    const updateUserButton = document.getElementById('updateUser');
    const clearFormButton = document.getElementById('clearForm');
    const loadUsersButton = document.getElementById('loadUsers');
    const searchButton = document.getElementById('searchButton');
    const searchQueryInput = document.getElementById('searchQuery');
    const userList = document.getElementById('userList');
    const statusDiv = document.getElementById('status');

    const displayUsers = (users) => {
        userList.innerHTML = '';
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = `Name: ${user.name}, Age: ${user.age}, Balance: ${user.balance}`;
            const editButton = document.createElement('button');
            editButton.textContent = 'Edit';
            editButton.addEventListener('click', () => {
                userIdInput.value = user.id;
                nameInput.value = user.name;
                ageInput.value = user.age;
                balanceInput.value = user.balance;
                createUserButton.style.display = 'none';
                updateUserButton.style.display = 'inline';
            });
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.addEventListener('click', () => {
                fetch(`http://127.0.0.1:5000/users/${user.id}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    statusDiv.textContent = data.message;
                })
                .catch(error => {
                    statusDiv.textContent = 'Error deleting user';
                });
            });
            li.appendChild(editButton);
            li.appendChild(deleteButton);
            userList.appendChild(li);
        });
    };

    const loadUsers = () => {
        fetch('http://127.0.0.1:5000/users')
            .then(response => response.json())
            .then(users => {
                displayUsers(users);
            })
            .catch(error => {
                statusDiv.textContent = 'Error loading users';
            });
    };

    createUserButton.addEventListener('click', () => {
        const user = {
            name: nameInput.value,
            age: parseInt(ageInput.value),
            balance: parseFloat(balanceInput.value)
        };
        fetch('http://127.0.0.1:5000/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(user)
        })
        .then(response => response.json())
        .then(data => {
            statusDiv.textContent = 'User created successfully';
            userForm.reset();
        })
        .catch(error => {
            statusDiv.textContent = 'Error creating user';
        });
    });

    updateUserButton.addEventListener('click', () => {
        const user = {
            name: nameInput.value,
            age: parseInt(ageInput.value),
            balance: parseFloat(balanceInput.value)
        };
        const userId = userIdInput.value;
        fetch(`http://127.0.0.1:5000/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(user)
        })
        .then(response => response.json())
        .then(data => {
            statusDiv.textContent = 'User updated successfully';
            userForm.reset();
            createUserButton.style.display = 'inline';
            updateUserButton.style.display = 'none';
        })
        .catch(error => {
            statusDiv.textContent = 'Error updating user';
        });
    });

    clearFormButton.addEventListener('click', () => {
        userForm.reset();
        createUserButton.style.display = 'inline';
        updateUserButton.style.display = 'none';
    });

    loadUsersButton.addEventListener('click', loadUsers);

    searchButton.addEventListener('click', () => {
        const query = searchQueryInput.value;
        fetch(`http://127.0.0.1:5000/users?search=${query}`)
            .then(response => response.json())
            .then(users => {
                displayUsers(users);
            })
            .catch(error => {
                statusDiv.textContent = 'Error searching users';
            });
    });

    socket.on('user_update', (data) => {
        displayUsers(data.users);
    });

    loadUsers();
});
"""

# Flask app content
app_content = """
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
        users = cursor.fetchall()
        return [{'id': user[0], 'name': user[1], 'age': user[2], 'balance': user[3]} for user in users]

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/users', methods=['GET'])
def get_users():
    search_query = request.args.get('search', '')
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if search_query:
            cursor.execute('SELECT * FROM users WHERE name LIKE ?', ('%' + search_query + '%',))
        else:
            cursor.execute('SELECT * FROM users')
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
        socketio.emit('user_update', {'users': _get_all_users_as_list()})
        return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance}), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if user:
            return jsonify({'id': user[0], 'name': user[1], 'age': user[2], 'balance': user[3]})
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
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        socketio.emit('user_update', {'users': _get_all_users_as_list()})
        return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        socketio.emit('user_update', {'users': _get_all_users_as_list()})
        return jsonify({'message': 'User deleted successfully'})

@socketio.on('connect')
def handle_connect():
    emit('user_update', {'users': _get_all_users_as_list()})

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
"""

# Create files
with open('index.html', 'w') as f:
    f.write(html_content)

with open('style.css', 'w') as f:
    f.write(css_content)

with open('script.js', 'w') as f:
    f.write(js_content)

with open('app.py', 'w') as f:
    f.write(app_content)

print("Files generated successfully. To run the application, execute: python app.py")