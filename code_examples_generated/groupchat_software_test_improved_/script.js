document.addEventListener('DOMContentLoaded', () => {
    const socket = io('http://127.0.0.1:5000');

    const userForm = document.getElementById('userForm');
    const userIdInput = document.getElementById('userId');
    const nameInput = document.getElementById('name');
    const ageInput = document.getElementById('age');
    const balanceInput = document.getElementById('balance');
    const createUserBtn = document.getElementById('createUserBtn');
    const updateUserBtn = document.getElementById('updateUserBtn');
    const clearFormBtn = document.getElementById('clearFormBtn');
    const loadUsersBtn = document.getElementById('loadUsersBtn');
    const searchInput = document.getElementById('search');
    const searchBtn = document.getElementById('searchBtn');
    const userList = document.getElementById('userList');
    const statusDiv = document.getElementById('status');

    function displayUsers(users) {
        userList.innerHTML = '';
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = `Name: ${user.name}, Age: ${user.age}, Balance: ${user.balance}`;
            const editBtn = document.createElement('button');
            editBtn.textContent = 'Edit';
            editBtn.addEventListener('click', () => editUser(user));
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = 'Delete';
            deleteBtn.addEventListener('click', () => deleteUser(user.id));
            li.appendChild(editBtn);
            li.appendChild(deleteBtn);
            userList.appendChild(li);
        });
    }

    function showMessage(message, isError = false) {
        statusDiv.textContent = message;
        statusDiv.style.color = isError ? 'red' : 'green';
    }

    socket.on('user_update', (data) => {
        displayUsers(data);
        showMessage('User list updated in real-time.');
    });

    userForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const user = {
            name: nameInput.value,
            age: parseInt(ageInput.value, 10),
            balance: parseFloat(balanceInput.value)
        };
        if (userIdInput.value) {
            updateUser(userIdInput.value, user);
        } else {
            createUser(user);
        }
    });

    clearFormBtn.addEventListener('click', () => {
        userIdInput.value = '';
        nameInput.value = '';
        ageInput.value = '';
        balanceInput.value = '';
        updateUserBtn.style.display = 'none';
        createUserBtn.style.display = 'inline-block';
    });

    loadUsersBtn.addEventListener('click', loadUsers);
    searchBtn.addEventListener('click', searchUsers);

    function loadUsers() {
        fetch('http://127.0.0.1:5000/users')
            .then(response => response.json())
            .then(data => displayUsers(data))
            .catch(error => showMessage('Error loading users', true));
    }

    function searchUsers() {
        const query = searchInput.value;
        fetch(`http://127.0.0.1:5000/users?search=${query}`)
            .then(response => response.json())
            .then(data => displayUsers(data))
            .catch(error => showMessage('Error searching users', true));
    }

    function createUser(user) {
        fetch('http://127.0.0.1:5000/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(user)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to create user');
            }
        })
        .then(data => {
            showMessage('User created successfully');
            clearFormBtn.click();
        })
        .catch(error => showMessage(error.message, true));
    }

    function editUser(user) {
        userIdInput.value = user.id;
        nameInput.value = user.name;
        ageInput.value = user.age;
        balanceInput.value = user.balance;
        createUserBtn.style.display = 'none';
        updateUserBtn.style.display = 'inline-block';
    }

    function updateUser(id, user) {
        fetch(`http://127.0.0.1:5000/users/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(user)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to update user');
            }
        })
        .then(data => {
            showMessage('User updated successfully');
            clearFormBtn.click();
        })
        .catch(error => showMessage(error.message, true));
    }

    function deleteUser(id) {
        fetch(`http://127.0.0.1:5000/users/${id}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                showMessage('User deleted successfully');
            } else {
                throw new Error('Failed to delete user');
            }
        })
        .catch(error => showMessage(error.message, true));
    }

    loadUsers();
});
