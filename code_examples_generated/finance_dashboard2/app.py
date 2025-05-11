
from flask import Flask
from flask_cors import CORS
from routes.auth import auth_blueprint
from routes.transactions import transactions_blueprint
from routes.budgets import budgets_blueprint
from routes.goals import goals_blueprint

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
app.register_blueprint(transactions_blueprint, url_prefix='/api/transactions')
app.register_blueprint(budgets_blueprint, url_prefix='/api/budgets')
app.register_blueprint(goals_blueprint, url_prefix='/api/goals')

if __name__ == '__main__':
    app.run(debug=True)
