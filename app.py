import dotenv
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Import routes
from chat_routes import chat_blueprint
from agent_routes import agent_blueprint
from user_routes import user_blueprint
from team_routes import team_blueprint

# Import socket handlers to register them
from socket_handlers import register_socket_handlers

# Load environment variables
dotenv.load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app, origins="http://localhost:5173")

# Setup SocketIO
socket_io = SocketIO(
    app, 
    cors_allowed_origins=["http://localhost:5173"],
)

# Register blueprints
app.register_blueprint(chat_blueprint)
app.register_blueprint(agent_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(team_blueprint)

# Register socket handlers
register_socket_handlers(socket_io)

if __name__ == '__main__':
    socket_io.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)