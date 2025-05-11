from flask import request
import autogen
from agents import WebSocketUserProxy
from config import LLM_CONFIG, ACTIVE_SESSIONS
from db_connection import connect_to_database
from utils import refactor_agent_name
from agents import agent_one
# Used to troublshoot websockets
import traceback

def register_socket_handlers(socket_io): # socket_io is the initialised instance in app.py

    #Called when websocket connection is made
    @socket_io.on('connect')
    def handle_connect():
        #Used for troubleshooting
        print(f"Client connected: {request.sid}")
        socket_io.emit('connection_status', {'status': 'connected', 'session_id': request.sid}, room=request.sid) # Emit to the connecting client

    #Called when websocket is disconnected
    @socket_io.on('disconnect')
    def handle_disconnect():
         #Used for troubleshooting
         print(f"Client disconnected: {request.sid}")
         #check and ensure the request sid is removed from Active Session {}.
         #Had issues reconnecting to websocket when ititial connection is diconnected and then try reconnecting
         if request.sid in ACTIVE_SESSIONS:
            del ACTIVE_SESSIONS[request.sid]
            print(f"Session {request.sid} removed from active sessions.")

    def get_or_create_session_agents(session_id):
        #Retrieves or creates agents for given Socketio session id
        if session_id not in ACTIVE_SESSIONS:
            print(f"Creating new agents for session: {session_id}")

            # Create the WebSocketUserProxy instance
            user_proxy = WebSocketUserProxy(
                session_id=session_id,
                socketio_instance=socket_io,
                name="User_Proxy",
                system_message="You are the user proxy. Relay messages clearly.",
                
                human_input_mode="NEVER",
                # max_consecutive_auto_reply=1, # Often set low for turn-based
                code_execution_config={
                    "work_dir": "groupchat", 
                    "use_docker": False,
                },
                # Check if the message content ends with TERMINATE
                is_termination_msg=lambda x: isinstance(x, dict) and x.get("content", "").rstrip().endswith("TERMINATE"),
            )

            # Autogen Assistant Agent
            assistant = autogen.AssistantAgent(
                name="MultiTalentAgent",
                system_message="You are a helpful AI assistant. Generate a concise and relevant response based *only* on the most recent user message in the conversation history. Do not repeat or append previous responses unless specifically asked to summarize. Reply with TERMINATE when the task is fully complete.",
                llm_config=LLM_CONFIG,
            )
            ACTIVE_SESSIONS[session_id] = {
                "user_proxy": user_proxy,
                "assistant": assistant,
            }
            print(f"Agents created for session {session_id}")
        else:
            print(f"Using existing agents for session: {session_id}")
        return ACTIVE_SESSIONS[session_id]["user_proxy"], ACTIVE_SESSIONS[session_id]["assistant"]

    # Called on user message - client sends message with event called user_message
    @socket_io.on('user_message')
    def handle_user_message(data):
        session_id = request.sid
        print(f"Received message from {session_id}: {data.get('message')}")

        try:
            user_input = data.get('message')
            if not user_input:
                socket_io.emit('error', {'error': 'No message content provided'}, room=session_id)
                return

            # Get agents for this session
            if session_id not in ACTIVE_SESSIONS:
                print(f"ERROR: No agents found for session {session_id}. Re-initializing.")
                get_or_create_session_agents(session_id) # Attempt re-initialization

            user_proxy, assistant = ACTIVE_SESSIONS[session_id]["user_proxy"], ACTIVE_SESSIONS[session_id]["assistant"]

            socket_io.emit('processing_status', {'status': 'processing'}, room=session_id)

            # Add user message to the assistant's chat history with the proxy
            # This ensures the assistant knows about the latest input.
            # Manipulate the assistants message storage.
            assistant.chat_messages.setdefault(user_proxy, []).append(
                {"role": "user", "content": user_input}
            )
            # Add to proxy history
            user_proxy.chat_messages.setdefault(assistant, []).append(
                {"role": "user", "content": user_input} 
            )


            # Generate the reply using the assistants updayed history
            assistant_reply = assistant.generate_reply(
                # proxy messages 
                messages=assistant.chat_messages[user_proxy],
                # Identify the sender for context
                sender=user_proxy, 
                config=LLM_CONFIG 
            )

            # Send the assistant's reply to the user proxy.
            # The proxy's overridden receive method will handle emitting it.
            user_proxy.receive( 
                message=assistant_reply,
                sender=assistant,
                request_reply=False
            )
            # The super().receive call inside WebSocketUserProxy.receive will handle
            # adding the assistant's reply to the proxys history.

            #Check for termination based on the assistant's reply
            is_terminate = user_proxy._is_termination_msg(assistant_reply)
            
            status_message = 'completed_terminated' if is_terminate else 'completed_waiting_next'
            socket_io.emit('processing_status', {'status': status_message}, room=session_id)
            if is_terminate:
                print(f"Termination message {session_id}")


        except Exception as e:
            print(f"Error processing message {session_id}: {str(e)}")
            traceback.print_exc()
            socket_io.emit('error', {'error': f"An error occurred: {str(e)}"}, room=session_id)
            socket_io.emit('processing_status', {'status': 'error'}, room=session_id) 

        def handle_user_message(data):
            session_id = request.sid
            print(f"Received message from {session_id}: {data.get('message')}")

            try:
                user_input = data.get('message')
                if not user_input:
                    socket_io.emit('error', {'error': 'No message content provided'}, room=session_id)
                    return

                # Get or create agents for this specific session
                user_proxy, assistant = get_or_create_session_agents(session_id)

                # Emit processing status once
                socket_io.emit('processing_status', {'status': 'processing'}, room=session_id)

                # Use the user_proxy to send the message To the assistant.
                user_proxy.send(
                    message=user_input,
                    recipient=assistant,
                    request_reply=True,
                    silent=False,
                )

                # Check if the last message received by the proxy was a termination message
                last_msg = user_proxy.last_message(assistant)
                if user_proxy._is_termination_msg(last_msg):
                    print(f"Termination message detected for session {session_id}")
                    socket_io.emit('processing_status', {'status': 'completed_terminated'}, room=session_id)
                else:
                    socket_io.emit('processing_status', {'status': 'completed_waiting_next'}, room=session_id)

            except Exception as e:
                print(f"Error processing message for session {session_id}: {str(e)}")
                traceback.print_exc()
                socket_io.emit('error', {'error': f"An internal error occurred: {str(e)}"}, room=session_id)
                socket_io.emit('processing_status', {'status': 'error'}, room=session_id)


    @socket_io.on('user_message_team')
    def handle_team_chat_message(data):
        
        print(f"Received message for team chat from {request.sid}: {data['message']}")
        session_id = request.sid

        try:
            message = data['message']
            agentOneId = data.get('agentOne')
            agentTwoId = data.get('agentTwo')
            agentThreeId = data.get('agentThree')
            
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

            #verify 3 agents are returned 
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
            # The user_proxy will use self.socket_io to emit messages when its receive method is called
            user_proxy.initiate_chat(manager, message=message)

            # Send completion status
            socket_io.emit('processing_status', {'status': 'completed'}, room=session_id)

        except Exception as e:
            print(f"Error processing team message: {str(e)}")
            #Emmit error if one occurs
            socket_io.emit('error', {'error': str(e)}, room=session_id)
