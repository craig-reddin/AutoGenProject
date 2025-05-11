
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
