from flask import Blueprint, request, jsonify

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/', methods=['GET'])
def get_transactions():
    # Fetch transactions
    return jsonify([])

@transactions_bp.route('/', methods=['POST'])
def add_transaction():
    # Add a new transaction
    return jsonify({'message': 'Transaction added successfully.'}), 201

@transactions_bp.route('/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def transaction(id):
    if request.method == 'GET':
        # Fetch a specific transaction
        return jsonify({})
    elif request.method == 'PUT':
        # Update a specific transaction
        return jsonify({'message': 'Transaction updated successfully.'}), 200
    elif request.method == 'DELETE':
        # Delete a specific transaction
        return jsonify({'message': 'Transaction deleted successfully.'}), 200
