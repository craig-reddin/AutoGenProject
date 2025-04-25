from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Import routes
from chat_routes import chat_blueprint
from agent_routes import agent_blueprint
from user_routes import user_blueprint
from team_routes import team_blueprint
from socket_handlers import register_socket_handlers 


# Create Flask app
app = Flask(__name__)
#wrap app in CORS - allow communication for the default localhost of my react application
CORS(app, origins="http://localhost:5173")

# Setup SocketIO
socket_io = SocketIO(
    app, 
    cors_allowed_origins=["http://localhost:5173"],
)

# Register blueprints - allow access to application endpoints.
app.register_blueprint(chat_blueprint)
app.register_blueprint(agent_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(team_blueprint)

# Register socket handlers - pass initialised socketio
register_socket_handlers(socket_io)

#run application, ensure host 0.0.0.0 on port 5000 for websocket communication
#HTTP requests will occur on host 127.0.0.1 on port 5000
#reloader set to false to ensure application does not reload due to user proxy file creation causing the application to reload.
if __name__ == '__main__':
    socket_io.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
