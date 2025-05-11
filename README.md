GenAIColab - Autonomous Multi-Agent Chat Application

GenAIColab is my final year project for NCI (National College of Ireland). It's a multi-agent chat system where users can create and interact with LLM agents, with both single and team chats implemented.

The application allows:

Chatting with AI agents (powered by OpenAI's GPT-4o model)
Creating custom AI agents with different specialisations
Configuring teams of agents that work together autonomously
Real-time conversations using WebSockets
Saving and revisiting previous chats

Stack used:

Backend:

Flask - Python web framework
Flask-SocketIO - Real-time WebSocket communication
AutoGen - Microsoft's framework for multi-agent conversations
PostgreSQL - Database for storing users, agents, chats, and teams
OpenAI API - Model gpt-4o leveraged

Frontend:

React Vite - https://github.com/craig-reddin/Specialised_Agents_Frontend.git

Other technologies:

Auth0 - User authentication
pytest - Unit testing
python-dotenv - Environment variable management

Features

1. Single Agent Chat

Unconfigured single agent. 

2. Team Chat

Teams of 3 agents with different specialisations
Agents collaborate to solve complex problems
Group chat management with automatic agent selection

3. Custom Agents

Create agents with specific specialisations
Configure agent behaviour with custom prompts
System hardcoded agents also available to all users

4. Chat Management

Save chat conversations
View previous chats
Delete chats

5. User Management

Auth0 integration for secure login
User profile management
Account deletion with deletion of all user data

Prerequisites

AutoGen - 0.4.1
Python - 3.12.6
PostgreSQL database - 17.2
OpenAI API key - Topped Up Account
Auth0 account
Flask - 2.2.3
Flask SocketIO - 5.1.1 
Dotenv - 1.1.0
Flast Cors - 5.0.0
Pystest - 8.3.5

Installation

Clone the repository:

git clone https://github.com/craig-reddin/AutoGenProject.git

cd AutoGenProject'

Install dependencies

Install AutoGen
pip install autogen==0.4.1

Install Flask and Flask extensions
pip install Flask==2.2.3
pip install Flask-SocketIO==5.1.1
pip install Flask-Cors==5.0.0

Install python-dotenv
pip install python-dotenv==1.1.0

Install PostgreSQL 
pip install psycopg2

Install OpenAI Python
pip install openai

Install Auth0 Python
pip install auth0-python


Set up environment variables:
Create a .env file in the root directory:

OPEN_AI_KEY=your_openai_api_key
POSTGRES_PASSWORD=your_db_password
DATABASE_NAME=your_db_name
DATABASE_HOST= your_host_name
DATABASE_USERNAME=your_db_username
DATABASE_PORT=5432

Set up PostgreSQL database with the following tables:

usertable - Stores user information
agentdata - Stores agent configurations
chattable - Stores chat conversations
agentteams - Stores team configurations


Run the application:

python app.py
The server starts on http://127.0.0.1:5000
API Endpoints 

/chat - Individual agent chat
/chat_team - Team chat
/get_previous_chat - Retrieve saved chat
/gather_previous_chat_names - List user's chats
/store_chat - Save chat conversation
/delete_chat - Delete a chat

