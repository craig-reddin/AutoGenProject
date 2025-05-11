from flask import Blueprint, request, jsonify

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/', methods=['GET'])
def get_budgets():
    # Fetch budgets
    return jsonify([])

@budgets_bp.route('/', methods=['POST'])
def add_budget():
    # Add a new budget
    return jsonify({'message': 'Budget added successfully.'}), 201

@budgets_bp.route('/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def budget(id):
    if request.method == 'GET':
        # Fetch a specific budget
        return jsonify({})
    elif request.method == 'PUT':
        # Update a specific budget
        return jsonify({'message': 'Budget updated successfully.'}), 200
    elif request.method == 'DELETE':
        # Delete a specific budget
        return jsonify({'message': 'Budget deleted successfully.'}), 200
