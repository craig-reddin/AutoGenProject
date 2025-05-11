
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
