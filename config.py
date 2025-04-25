import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Environment variables
OPENAIKEY = os.getenv('OPEN_AI_KEY')
DATABASE_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PORT = os.getenv('DATABASE_PORT')


# Agent configuration
LLM_CONFIG = {
    # Temperature determines the creativity of response
    "temperature": 0,
    # Config list to pass agent model and api key
    "config_list": [{"model": 'gpt-4o', 'api_key': OPENAIKEY}],
    # Currently set to none - will configure according after testing
    "timeout": None,
}

# Track active chat sessions - used for websockets
ACTIVE_SESSIONS = {}
