
const socket = io('http://127.0.0.1:5000');

document.addEventListener('DOMContentLoaded', () => {
    const userForm = document.getElementById('userForm');
    const userIdInput = document.getElementById('userId');
    const nameInput = document.getElementById('name');
    const ageInput = document.getElementById('age');
    const balanceInput = document.getElementById('balance');
    const createUserBtn = document.getElementById('createUserBtn');
    const updateUserBtn = document.getElementById('updateUserBtn');
    const clearFormBtn = document.getElementById('clearFormBtn');
    const searchBtn = document.getElementById('searchBtn');
    const loadUsersBtn = document.getElementById('loadUsersBtn');
    const statusDiv = document.getElementById('status');
    const userList = document.getElementById('userList');

    const apiUrl = 'http://127.0.0.1:5000/users';

    const displayUsers = (users) => {
        userList.innerHTML = '';
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = `${user.name}, Age: ${user.age}, Balance: $${user.balance}`;
            const editBtn = document.createElement('button');
            editBtn.textContent = 'Edit';
            editBtn.addEventListener('click', () => {
                userIdInput.value = user.id;
                nameInput.value = user.name;
                ageInput.value = user.age;
                balanceInput.value = user.balance;
                createUserBtn.hidden = true;
                updateUserBtn.hidden = false;
            });
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = 'Delete';
            deleteBtn.addEventListener('click', () => {
                deleteUser(user.id);
            });
            li.appendChild(editBtn);
            li.appendChild(deleteBtn);
            userList.appendChild(li);
        });
    };

    const loadUsers = async () => {
        try {
            const response = await fetch(apiUrl);
            const data = await response.json();
            displayUsers(data);
        } catch (error) {
            console.error('Error loading users:', error);
            statusDiv.textContent = 'Error loading users';
        }
    };

    const createUser = async () => {
        const name = nameInput.value;
        const age = ageInput.value;
        const balance = balanceInput.value;
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, age, balance })
            });
            const data = await response.json();
            if (response.ok) {
                statusDiv.textContent = 'User created successfully';
                userForm.reset();
                socket.emit('user_update');
            } else {
                statusDiv.textContent = `Error: ${data.message}`;
            }
        } catch (error) {
            console.error('Error creating user:', error);
            statusDiv.textContent = 'Error creating user';
        }
    };

    const updateUser = async () => {
        const id = userIdInput.value;
        const name = nameInput.value;
        const age = ageInput.value;
        const balance = balanceInput.value;
        try {
            const response = await fetch(`${apiUrl}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, age, balance })
            });
            const data = await response.json();
            if (response.ok) {
                statusDiv.textContent = 'User updated successfully';
                userForm.reset();
                createUserBtn.hidden = false;
                updateUserBtn.hidden = true;
                socket.emit('user_update');
            } else {
                statusDiv.textContent = `Error: ${data.message}`;
            }
        } catch (error) {
            console.error('Error updating user:', error);
            statusDiv.textContent = 'Error updating user';
        }
    };

    const deleteUser = async (id) => {
        try {
            const response = await fetch(`${apiUrl}/${id}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            if (response.ok) {
                statusDiv.textContent = 'User deleted successfully';
                socket.emit('user_update');
            } else {
                statusDiv.textContent = `Error: ${data.message}`;
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            statusDiv.textContent = 'Error deleting user';
        }
    };

    socket.on('user_update', loadUsers);

    createUserBtn.addEventListener('click', createUser);
    updateUserBtn.addEventListener('click', updateUser);
    clearFormBtn.addEventListener('click', () => userForm.reset());
    searchBtn.addEventListener('click', loadUsers);
    loadUsersBtn.addEventListener('click', loadUsers);

    loadUsers();
});
