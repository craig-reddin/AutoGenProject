# filename: generate_app.py

import os

# HTML content for index.html
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Management</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>User Management</h1>
        <div class="form-container">
            <input type="text" id="search" placeholder="Search users...">
            <button id="searchButton">Search</button>
            <form id="userForm">
                <input type="hidden" id="userId">
                <input type="text" id="name" placeholder="Name" required>
                <input type="number" id="age" placeholder="Age" min="0" required>
                <input type="number" id="balance" placeholder="Balance" step="0.01" min="0" required>
                <button type="submit" id="createUserButton">Create User</button>
                <button type="button" id="updateUserButton" style="display:none;">Update User</button>
                <button type="button" id="clearFormButton">Clear Form</button>
            </form>
            <button id="loadUsersButton">Load Users</button>
        </div>
        <div id="statusMessage"></div>
        <div id="userList"></div>
    </div>
    <script src="script.js"></script>
</body>
</html>
"""

# CSS content for style.css
css_content = """body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f4f4f9;
}

.container {
    width: 80%;
    max-width: 600px;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.form-container {
    margin-bottom: 20px;
}

input, button {
    margin: 5px 0;
    padding: 10px;
    width: 100%;
    box-sizing: border-box;
}

button {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

#userList {
    margin-top: 20px;
}

.user-row {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    border-bottom: 1px solid #ddd;
}

.user-row:nth-child(even) {
    background-color: #f9f9f9;
}
"""

# JavaScript content for script.js
js_content = """document.addEventListener('DOMContentLoaded', function() {
    const apiUrl = 'http://127.0.0.1:5000/users';

    const userForm = document.getElementById('userForm');
    const userIdInput = document.getElementById('userId');
    const nameInput = document.getElementById('name');
    const ageInput = document.getElementById('age');
    const balanceInput = document.getElementById('balance');
    const createUserButton = document.getElementById('createUserButton');
    const updateUserButton = document.getElementById('updateUserButton');
    const clearFormButton = document.getElementById('clearFormButton');
    const loadUsersButton = document.getElementById('loadUsersButton');
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('search');
    const statusMessage = document.getElementById('statusMessage');
    const userList = document.getElementById('userList');

    function displayStatus(message, isError = false) {
        statusMessage.textContent = message;
        statusMessage.style.color = isError ? 'red' : 'green';
    }

    function clearForm() {
        userIdInput.value = '';
        nameInput.value = '';
        ageInput.value = '';
        balanceInput.value = '';
        createUserButton.style.display = 'inline-block';
        updateUserButton.style.display = 'none';
    }

    function loadUsers(search = '') {
        fetch(`${apiUrl}?search=${encodeURIComponent(search)}`)
            .then(response => response.json())
            .then(users => {
                userList.innerHTML = '';
                users.forEach(user => {
                    const userRow = document.createElement('div');
                    userRow.className = 'user-row';
                    userRow.innerHTML = `
                        <span>${user.name} (Age: ${user.age}, Balance: $${user.balance.toFixed(2)})</span>
                        <div>
                            <button onclick="editUser(${user.id})">Edit</button>
                            <button onclick="deleteUser(${user.id})">Delete</button>
                        </div>
                    `;
                    userList.appendChild(userRow);
                });
            })
            .catch(error => displayStatus('Error loading users', true));
    }

    function editUser(id) {
        fetch(`${apiUrl}/${id}`)
            .then(response => response.json())
            .then(user => {
                userIdInput.value = user.id;
                nameInput.value = user.name;
                ageInput.value = user.age;
                balanceInput.value = user.balance;
                createUserButton.style.display = 'none';
                updateUserButton.style.display = 'inline-block';
            })
            .catch(error => displayStatus('Error loading user', true));
    }

    function deleteUser(id) {
        fetch(`${apiUrl}/${id}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(result => {
                displayStatus(result.message);
                loadUsers();
            })
            .catch(error => displayStatus('Error deleting user', true));
    }

    userForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const id = userIdInput.value;
        const name = nameInput.value.trim();
        const age = parseInt(ageInput.value, 10);
        const balance = parseFloat(balanceInput.value);

        if (!name) {
            displayStatus('Name is required', true);
            return;
        }

        if (isNaN(age) || age < 0) {
            displayStatus('Age must be a positive number', true);
            return;
        }

        if (isNaN(balance) || balance < 0) {
            displayStatus('Balance must be a non-negative number', true);
            return;
        }

        const userData = { name, age, balance };

        if (id) {
            fetch(`${apiUrl}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            })
            .then(response => response.json())
            .then(user => {
                displayStatus(`User '${user.name}' updated.`);
                clearForm();
                loadUsers();
            })
            .catch(error => displayStatus('Error updating user', true));
        } else {
            fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            })
            .then(response => response.json())
            .then(user => {
                displayStatus(`User '${user.name}' created.`);
                clearForm();
                loadUsers();
            })
            .catch(error => displayStatus('Error creating user', true));
        }
    });

    clearFormButton.addEventListener('click', clearForm);
    loadUsersButton.addEventListener('click', () => loadUsers());
    searchButton.addEventListener('click', () => loadUsers(searchInput.value));

    loadUsers();
});
"""

# Python content for app.py
app_content = """from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'users.db'

def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    balance REAL
                )
            ''')

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/users', methods=['GET'])
def get_users():
    search = request.args.get('search', '')
    query = 'SELECT * FROM users WHERE name LIKE ?'
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute(query, ('%' + search + '%',))
        users = [{'id': row[0], 'name': row[1], 'age': row[2], 'balance': row[3]} for row in cursor.fetchall()]
    return jsonify(users)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    name = data.get('name', '').strip()
    age = data.get('age')
    balance = data.get('balance')

    if not name:
        return jsonify({'error': 'Name is required'}), 400
    if not isinstance(age, int) or age < 0:
        return jsonify({'error': 'Age must be a positive integer'}), 400
    if not isinstance(balance, (int, float)) or balance < 0:
        return jsonify({'error': 'Balance must be a non-negative number'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('INSERT INTO users (name, age, balance) VALUES (?, ?, ?)', (name, age, balance))
        user_id = cursor.lastrowid
        conn.commit()

    return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance}), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return jsonify({'id': row[0], 'name': row[1], 'age': row[2], 'balance': row[3]})
        else:
            return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    name = data.get('name', '').strip()
    age = data.get('age')
    balance = data.get('balance')

    if not name:
        return jsonify({'error': 'Name is required'}), 400
    if not isinstance(age, int) or age < 0:
        return jsonify({'error': 'Age must be a positive integer'}), 400
    if not isinstance(balance, (int, float)) or balance < 0:
        return jsonify({'error': 'Balance must be a non-negative number'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('UPDATE users SET name = ?, age = ?, balance = ? WHERE id = ?', (name, age, balance, user_id))
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        conn.commit()

    return jsonify({'id': user_id, 'name': name, 'age': age, 'balance': balance})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        conn.commit()

    return jsonify({'message': 'User deleted'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
"""

# Function to write content to a file
def write_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

# Generate the files
write_file('index.html', html_content)
write_file('style.css', css_content)
write_file('script.js', js_content)
write_file('app.py', app_content)

# Instructions for the user
print("Files generated successfully.")
print("To run the application, execute: python app.py")
print("Access the application at: http://127.0.0.1:5000")
print("Ensure you have Flask and Flask-Cors installed: pip install Flask Flask-Cors")