from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth import auth_bp
from routes.transactions import transactions_bp
from routes.budgets import budgets_bp
from routes.goals import goals_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
app.register_blueprint(budgets_bp, url_prefix='/api/budgets')
app.register_blueprint(goals_bp, url_prefix='/api/goals')

if __name__ == '__main__':
    app.run(debug=True)
