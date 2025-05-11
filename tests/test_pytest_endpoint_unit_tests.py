# test_endpoints.py
import pytest
import json
from app import app
from unittest.mock import MagicMock
from config import ACTIVE_SESSIONS

@pytest.fixture
def client():
    #Create a test client for the app
    #Configure flask app into Testing mode for testing functionality.
    app.config['TESTING'] = True
    #Mock the client
    with app.test_client() as client:
        yield client

#Mock database connection
@pytest.fixture
def mock_db_connection(monkeypatch):
    #Mock the database connection
    mock_conn = MagicMock()
    #Mock the cursor
    mock_cursor = MagicMock()
    #"Update" mcok_con state 
    mock_conn.cursor.return_value = mock_cursor
    
    # Function returning the mock connection
    def mock_connect_to_database():
        return mock_conn
    
    #  Replace the connect_to_database mathod with mock_connect_to_database, ensuring no actual transactions occur  
     
    monkeypatch.setattr('chat_routes.connect_to_database', mock_connect_to_database)
    monkeypatch.setattr('agent_routes.connect_to_database', mock_connect_to_database)
    monkeypatch.setattr('user_routes.connect_to_database', mock_connect_to_database)
    monkeypatch.setattr('team_routes.connect_to_database', mock_connect_to_database)
    monkeypatch.setattr('socket_handlers.connect_to_database', mock_connect_to_database)
    
    #return both mock cursor and conn
    return mock_conn, mock_cursor

# Mock autogen functionality
@pytest.fixture
def mock_autogen(monkeypatch):

    #initialise magig mock object - 
    mock_user_proxy = MagicMock()
    mock_agent = MagicMock()

    # Mock the chat_messages attribute and the clear method
    mock_chat_messages = MagicMock()
    mock_user_proxy.chat_messages = mock_chat_messages

    # Mock the initiate_chat method
    mock_user_proxy.initiate_chat.return_value = None

    # Create functions that return mock objects
    #**kwargs passed ensures the parameters required for the actualy object are fufilled. 
    def mock_assistant_agent(**kwargs):
        return mock_agent
    
    def mock_group_chat(**kwargs):
        return MagicMock()
    
    def mock_group_chat_manager(**kwargs):
        return MagicMock()

    # Replace autogen objects with mocks
    monkeypatch.setattr('chat_routes.user_proxy', mock_user_proxy)
    monkeypatch.setattr('chat_routes.agent_one', mock_assistant_agent)
    monkeypatch.setattr('autogen.AssistantAgent', mock_assistant_agent)
    monkeypatch.setattr('autogen.GroupChat', mock_group_chat)
    monkeypatch.setattr('autogen.GroupChatManager', mock_group_chat_manager)
    monkeypatch.setattr('agents.autogen.AssistantAgent', mock_assistant_agent)

    return mock_user_proxy, mock_agent

#==================== CHAT ROUTES TESTS ====================

def test_chat_endpoint(client, mock_autogen):
    #Test the /chat endpoint
    mock_user_proxy, mock_agent = mock_autogen

    response = client.post('/chat',
                             data=json.dumps({'message': 'Test message'}),
                             content_type='application/json')

    # Verify response is 200
    assert response.status_code == 200
    data = json.loads(response.data)
    #assery the paylod key - ensure it exists.
    assert 'response' in data

    # Verify mocks were called correctly (once)
    mock_user_proxy.initiate_chat.assert_called_once()
    # Assert the  clear method was called once - after chat completion
    mock_user_proxy.chat_messages.clear.assert_called_once()



def test_chat_team_endpoint(client, mock_db_connection, mock_autogen):
    #Test the /chat_team endpoint
    mock_conn, mock_cursor = mock_db_connection
    mock_user_proxy, mock_agent = mock_autogen
    
    # Set up the mock to return test data
    mock_cursor.fetchall.return_value = [
        ('AI Specialist', 'You are an AI expert'),
        ('Programming Expert', 'You are an coding expert'),
        ('Marketing Manager', 'You are a marketing manager') 
    ]

    #Mock client POST request
    response = client.post('/chat_team', 
                          data=json.dumps({
                              'message': 'Test team message',
                              'agentOne': '1',
                              'agentTwo': '2',
                              'agentThree': '3'
                          }),
                          content_type='application/json')
    
    # Verify response is 200
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    
    # Verify database query was called
    mock_cursor.execute.assert_called()
     # Verify mocks were called correctly (once)
    mock_user_proxy.initiate_chat.assert_called_once()
    # Assert the  clear method was called once - after chat completion
    mock_user_proxy.chat_messages.clear.assert_called_once()

def test_get_previous_chat(client, mock_db_connection):
    #Test the /get_previous_chat endpoint
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return a chat
    mock_cursor.fetchone.return_value = ['<div>Previous chat content</div>']
    
    response = client.post('/get_previous_chat', 
                          data=json.dumps({'chatName': 'Test Chat'}),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    
    # Verify database was queried properly
    mock_cursor.execute.assert_called_once()

def test_get_previous_chat_not_found(client, mock_db_connection):
    #Test the /get_previous_chat endpoit when chat is not found
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return None (chat not found)
    mock_cursor.fetchone.return_value = None
    
    response = client.post('/get_previous_chat', 
                          data=json.dumps({'chatName': 'Nonexistent Chat'}),
                          content_type='application/json')
    
    # Verify response contains error message
    assert response.status_code == 200
    response_data = "<div id='previous_chat_error'><h1 id='returned_data'>Error fetching chat data</h1><br /><h3 id='previous_chat_error_sub'>Please try again later</h3></div>"
    data = json.loads(response.data)
    assert 'message' in data
    assert response_data in data['message']

def test_gather_previous_chat_names(client, mock_db_connection):
    #Test the /gather_previous_chat_names endpoint
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return chat names
    mock_cursor.fetchall.return_value = [(['Chat 1', '01']), ('Chat 2', '02')]
    
    response = client.post('/gather_previous_chat_names', 
                          data=json.dumps({'email': 'test@ncirl.ie'}),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    
    # Verify database was queried properly
    mock_cursor.execute.assert_called_once()

def test_store_chat(client, mock_db_connection):
    #Test the /store_chat endpoint
    mock_conn, mock_cursor = mock_db_connection
    
    response = client.post('/store_chat', 
                          data=json.dumps({
                              'message': 'Test chat content',
                              'email': 'test@ncirl.ie',
                              'chat_name': 'Test Chat'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'Message stored'
    
    # Verify database insert was called
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

def test_delete_chat(client, mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    
    response = client.post('/delete_chat', 
                          data=json.dumps({
                              'email': 'test@ncirl.ie',
                              'chatName': 'Test Chat'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'Chat Deleted'
    
    # Verify database delete was called
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

# =============== AGENT ROUTES TESTS ========================

def test_create_agent(client, mock_db_connection):
    #Test the /create_agent endpoint
    mock_conn, mock_cursor = mock_db_connection
    
    response = client.post('/create_agent', 
                          data=json.dumps({
                              'email': 'test@ncirl.ie',
                              'specialisation': 'AI Expert',
                              'prompt': 'You are an AI expert'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Agent Created'
    
    # Verify database insert was called
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

def test_retrieve_agents(client, mock_db_connection):
    #Test the /retrieve_agents endpoint
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return agents
    mock_cursor.fetchall.return_value = [
        ('AI Expert', 'You are an AI expert', 1),
        ('Coding Expert', 'You are a coding expert', 2)
    ]
    
    response = client.post('/retrieve_agents', 
                          data=json.dumps({'email': 'test@ncirl.ie'}),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert len(data['message']) == 2  # Two agents returned
    
    # Verify database was queried properly
    mock_cursor.execute.assert_called_once()

def test_retrieve_agents_none_found(client, mock_db_connection):
    #Test the /retrieve_agents endpoint, no agents are found.
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return no agents
    mock_cursor.fetchall.return_value = []
    
    response = client.post('/retrieve_agents', 
                          data=json.dumps({'email': 'test@ncirl.ie'}),
                          content_type='application/json')
    
    # Verify response contains error message
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert "<div id='previous_chat_error'><h1 id='returned_data'>Could not fetch agent</h1><br /><h3 id='previous_chat_error_sub'>Please try again later</h3></div>" in data['message']

# ==================== USER ROUTES TESTS ====================

def test_sign_in_user_success(client, mock_db_connection):
    #Test the /sign_in_user endpoint with positive login
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return valid credentials
    mock_cursor.fetchone.return_value = ('test@ncirl.ie', 'password123')
    
    response = client.post('/sign_in_user', 
                          data=json.dumps({
                              'emailAddress': 'test@ncirl.ie',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'Sign in was successful'
    
    # Verify database was queried once
    mock_cursor.execute.assert_called_once()

def test_sign_in_user_incorrect_password(client, mock_db_connection):
    #Test the /sign_in_user endpoint with incorrect password
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return user but with different password
    mock_cursor.fetchone.return_value = ('test@ncirl.ie', 'correct_password')
    
    response = client.post('/sign_in_user', 
                          data=json.dumps({
                              'emailAddress': 'test@ncirl.ie',
                              'password': 'wrong_password'
                          }),

                      content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'Incorrect credentials'

def test_sign_in_user_not_found(client, mock_db_connection):
    #Test the /sign_in_user endpoint with user not found
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return no user
    mock_cursor.fetchone.return_value = None
    
    response = client.post('/sign_in_user', 
                          data=json.dumps({
                              'emailAddress': 'nonexistent@student.ncirl.ie',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'User not found'

def test_review_sign_in_existing_user(client, mock_db_connection):
    #Test the /review_sign_in endpoint with existing user
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return existing user
    mock_cursor.fetchone.return_value = ('test@ncirl.ie',)
    
    response = client.post('/review_sign_in', 
                          data=json.dumps({
                              'name': 'Test User',
                              'email': 'test@ncirl.ie'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'User Existed'
    
    # Verify create_user was not called (since user exists)
    mock_cursor.execute.assert_called_once()

def test_review_sign_in_new_user(client, mock_db_connection, monkeypatch):
    #Test the /review_sign_in endpoint with new user
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return no existing user
    mock_cursor.fetchone.return_value = None
    
    # Mock create_user function
    create_user_mock = MagicMock()
    monkeypatch.setattr('user_routes.create_user', create_user_mock)
    
    response = client.post('/review_sign_in', 
                          data=json.dumps({
                              'name': 'New User',
                              'email': 'new@ncirl.ie'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'User Created'
    
    # Verify create_user was called
    create_user_mock.assert_called_once_with('new@ncirl.ie', 'New User')

def test_delete_user(client, monkeypatch):
    # Test the /delete_user endpoint
    # Mock delete_user_flow function to return success
    mock_delete_flow = MagicMock(return_value=True)
    monkeypatch.setattr('user_routes.delete_user_flow', mock_delete_flow)
    
    response = client.post('/delete_user', 
                          data=json.dumps({
                              'email': 'test@ncirl.ie'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'User Deleted'
    
    # Verify delete_user_flow was called
    mock_delete_flow.assert_called_once_with('test@ncirl.ie')

def test_delete_user_failure(client, monkeypatch):
    #Test the /delete_user endpoint with deletion failure
    # Mock delete_user_flow function to return failure
    mock_delete_flow = MagicMock(return_value=False)
    monkeypatch.setattr('user_routes.delete_user_flow', mock_delete_flow)
    
    response = client.post('/delete_user', 
                          data=json.dumps({
                              'email': 'test@ncirl.ie'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'User Not Deleted'

# ==================== TEAM ROUTES TESTS ====================

def test_store_team(client, mock_db_connection):
    #Test the /store_team endpoint
    mock_conn, mock_cursor = mock_db_connection
    
    response = client.post('/store_team', 
                          data=json.dumps({
                              'teamName': 'AI Team',
                              'userEmail': 'test@ncirl.ie',
                              'teamDescription': 'A team of AI experts',
                              'agentOne': '1',
                              'agentTwo': '2',
                              'agentThree': '3'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == 'Team stored'
    
    # Verify database insert was called
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

def test_gather_teams(client, mock_db_connection):
    #Test the /gather_teams endpoint.
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up return teams mock
    mock_cursor.fetchall.return_value = [
        ('AI Team', 'A team of AI experts', '1', '2', '3'),
        ('AI Team2', 'A team of AI experts2', '4', '5', '6'),
    ]
    
    response = client.post('/gather_teams', 
                          data=json.dumps({
                              'email': 'test@ncirl.ie'
                          }),
                          content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert len(data['message']) == 2
    
    # Verify database was queried properly
    mock_cursor.execute.assert_called_once()

def test_gather_teams_none_found(client, mock_db_connection):
    #test the /gather_teams endpoint when no teams are found
    mock_conn, mock_cursor = mock_db_connection
    
    # Set up mock to return no teams
    mock_cursor.fetchall.return_value = []
    
    response = client.post('/gather_teams', 
                          data=json.dumps({
                              'email': 'test@ncirl.ie'
                          }),
                          content_type='application/json')
    
    # Verify response contains error message
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "<div id='previous_chat_error'><h1 id='returned_data'>Error fetching chat data</h1><br /><h3 id='previous_chat_error_sub'>Please try again later</h3></div>" in data['message']