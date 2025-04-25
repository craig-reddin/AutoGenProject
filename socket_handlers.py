from flask import request
import autogen
from agents import WebSocketUserProxy
from config import LLM_CONFIG, ACTIVE_SESSIONS
from db_connection import connect_to_database
from utils import refactor_agent_name
from agents import agent_one
# Used to troublshoot websockets
import traceback

def register_socket_handlers(socket_io): # socket_io is the initialised instance

    #Called when websocket connection is made
    @socket_io.on('connect')
    def handle_connect():
        #Used for troubleshooting
        print(f"Client connected: {request.sid}")
        socket_io.emit('connection_status', {'status': 'connected', 'session_id': request.sid}, room=request.sid) # Emit only to the connecting client

    #Called when websocket is disconnected
    @socket_io.on('disconnect')
    def handle_disconnect():
         #Used for troubleshooting
         print(f"Client disconnected: {request.sid}")
         #check and ensure the request sid is removed from Active Session {}.
         if request.sid in ACTIVE_SESSIONS:
            del ACTIVE_SESSIONS[request.sid]
            print(f"Session {request.sid} removed from active sessions.")


    #Called on event called user message - client sends message with even called user_message
    @socket_io.on('user_message')
    def handle_message(data):
        #User for troubleshooting
        print(f"Received message from {request.sid}: {data['message']}")
        session_id = request.sid

        try:
            #extract the message from the payload
            message = data['message']

            # Create the WebSocketUserProxy witht the overriden receive method.
            socket_user_proxy = WebSocketUserProxy(
                #pass the websocket session id
                session_id=session_id,
                #pass the socket
                socketio_instance=socket_io, # Pass the correct socket_io object
                #Pass the name
                name="User_proxy",
                
                human_input_mode="NEVER",
                
                max_consecutive_auto_reply=2,
                
                code_execution_config={
                    
                    "use_docker" : False,
                    # directory for files to be saved   
                    "work_dir": "groupchat",                 
                },
            )

            # Send acknowledgment - leveraged on the react front end using event listener
            socket_io.emit('processing_status', {'status': 'started'}, room=session_id)

            # Initiate chat - pass single agent and message
            socket_user_proxy.initiate_chat(agent_one, message=message)

            # Send completion status
            socket_io.emit('processing_status', {'status': 'completed'}, room=session_id)


        except Exception as e:
            print(f"Error processing message: {str(e)}")
            
            traceback.print_exc()
            # Ensure session_id is defined even in exceptions
            socket_io.emit('error', {'error': str(e)}, room=session_id)
            # return {'status': 'error', 'message': str(e)} # Optional return


    @socket_io.on('user_message_team')
    def handle_team_chat_message(data):
        
        print(f"Received message for team chat from {request.sid}: {data['message']}")
        session_id = request.sid

        try:
            message = data['message']
            agentOneId = data.get('agentOne')
            agentTwoId = data.get('agentTwo')
            agentThreeId = data.get('agentThree')
            print("Hello")
            
            # Send acknowledgment
            socket_io.emit('processing_status', {'status': 'started'}, room=session_id)

            print(f"Creating new session for {session_id}")
            # Create a proxy agent for this session
            #User proxy configuration is the exact same as in handle_message()
            user_proxy = WebSocketUserProxy(
            session_id=session_id,
            socketio_instance=socket_io, 
            name="User_proxy",                
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            code_execution_config={
                "use_docker" : False,
                "work_dir": "groupchat",                    
            },
        )

            #Get the data of the requiested agents to be inserted 
            conn = connect_to_database()
            try:
                cursor = conn.cursor()
                query = "SELECT agentspecialisation, agentconfig FROM agentdata WHERE agentid IN (%s, %s, %s)"
                cursor.execute(query, (agentOneId, agentTwoId, agentThreeId))
                result = cursor.fetchall()
                cursor.close()
            finally:
                conn.close()


            if len(result) == 3:
                #Unpack the results
                (specialisationOne, configOne), (specialisationTwo, configTwo), (specialisationThree, configThree) = result
                #refactor the names ensuring 
                nameOne = refactor_agent_name(specialisationOne)
                nameTwo = refactor_agent_name(specialisationTwo)
                nameThree = refactor_agent_name(specialisationThree)


                # Create assistant agents
                #The conversation is handled by the user proxy - socket io not required for these agents
                agent_one_team = autogen.AssistantAgent(name=nameOne, description=configOne, llm_config=LLM_CONFIG)
                agent_two_team = autogen.AssistantAgent(name=nameTwo, description=configTwo, llm_config=LLM_CONFIG)
                agent_three_team = autogen.AssistantAgent(name=nameThree, description=configThree, llm_config=LLM_CONFIG)

                # Setup group chat - same configuration as in chat_routes file - chat_team()
                groupchat = autogen.GroupChat(
                    agents=[user_proxy, agent_one_team, agent_two_team, agent_three_team],
                    messages=[],
                    max_round=12 
                )

                # Setup group chat manager - same configuration as in chat_routes file - chat_team() - no description
                manager = autogen.GroupChatManager(
                    groupchat=groupchat,
                    llm_config=LLM_CONFIG                        
                    
                )

                # Store the session data
                ACTIVE_SESSIONS[session_id] = {
                    'user_proxy': user_proxy,
                    'manager': manager,
                }
                
                print(f"Session {session_id} created and stored.")
            else:
                #Used for troubleshooting
                print(f"Error: Could not retrieve all agent configurations for IDs {agentOneId}, {agentTwoId}, {agentThreeId}")
                socket_io.emit('error', {'error': "Could not retrieve configurations for agents."}, room=session_id)
                # return if setup failed
                return 



            # Get the session data (user_proxy already has socket_io)
            session_data = ACTIVE_SESSIONS[session_id]
            user_proxy = session_data['user_proxy']
            manager = session_data['manager']

            # Initiate the chat
            # The user_proxy will use its stored self.socket_io to emit messages when its receive method is called
            user_proxy.initiate_chat(manager, message=message)

            # Send completion status
            socket_io.emit('processing_status', {'status': 'completed'}, room=session_id)

        except Exception as e:
            print(f"Error processing team message: {str(e)}")
            traceback.print_exc()
            #Emmit error if one occurs
            socket_io.emit('error', {'error': str(e)}, room=session_id)
