
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
    