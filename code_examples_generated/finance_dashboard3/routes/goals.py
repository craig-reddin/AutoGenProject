from flask import Blueprint, request, jsonify

goals_bp = Blueprint('goals', __name__)

@goals_bp.route('/', methods=['GET'])
def get_goals():
    # Fetch goals
    return jsonify([])

@goals_bp.route('/', methods=['POST'])
def add_goal():
    # Add a new goal
    return jsonify({'message': 'Goal added successfully.'}), 201

@goals_bp.route('/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def goal(id):
    if request.method == 'GET':
        # Fetch a specific goal
        return jsonify({})
    elif request.method == 'PUT':
        # Update a specific goal
        return jsonify({'message': 'Goal updated successfully.'}), 200
    elif request.method == 'DELETE':
        # Delete a specific goal
        return jsonify({'message': 'Goal deleted successfully.'}), 200
