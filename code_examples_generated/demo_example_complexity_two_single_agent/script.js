
    const socket = io('http://127.0.0.1:5000');

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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, age, balance })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('status').innerText = data.error;
            } else {
                clearForm();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function updateUser() {
        const id = document.getElementById('userId').value;
        const name = document.getElementById('name').value;
        const age = document.getElementById('age').value;
        const balance = document.getElementById('balance').value;
        fetch(`http://127.0.0.1:5000/users/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, age, balance })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('status').innerText = data.error;
            } else {
                clearForm();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function loadUsers() {
        fetch('http://127.0.0.1:5000/users')
        .then(response => response.json())
        .then(data => displayUsers(data))
        .catch(error => console.error('Error:', error));
    }

    function displayUsers(users) {
        const userList = document.getElementById('userList');
        userList.innerHTML = '';
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = `Name: ${user.name}, Age: ${user.age}, Balance: ${user.balance}`;
            userList.appendChild(li);
        });
    }

    function clearForm() {
        document.getElementById('userId').value = '';
        document.getElementById('name').value = '';
        document.getElementById('age').value = '';
        document.getElementById('balance').value = '';
        document.getElementById('updateUser').style.display = 'none';
        document.getElementById('createUser').style.display = 'inline';
    }
    