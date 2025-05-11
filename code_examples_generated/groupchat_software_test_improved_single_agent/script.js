
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
