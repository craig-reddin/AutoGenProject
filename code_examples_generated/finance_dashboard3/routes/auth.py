from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    # Handle user registration
    return jsonify({'message': 'User registered successfully.'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    # Handle user login
    return jsonify({'message': 'User logged in successfully.'}), 200

@auth_bp.route('/logout', methods=['GET'])
def logout():
    # Handle user logout
    return jsonify({'message': 'User logged out successfully.'}), 200

@auth_bp.route('/profile', methods=['GET', 'PUT'])
def profile():
    if request.method == 'GET':
        # Fetch user profile
        return jsonify({'username': 'testuser', 'email': 'test@example.com'})
    elif request.method == 'PUT':
        # Update user profile
        return jsonify({'message': 'Profile updated successfully.'}), 200
