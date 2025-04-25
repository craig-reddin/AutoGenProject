import os
import re
import autogen
from flask_socketio import SocketIO
from dotenv import load_dotenv

from config import LLM_CONFIG

load_dotenv()

# Basic user proxy agent for non-socket communications
user_proxy = autogen.UserProxyAgent(
    # Give user proxy a name
    name="User_proxy",
    # Execution parameter to be passed to proxy
    code_execution_config={
        # Directory to execute scripts and save files to.
        "work_dir": "groupchat",
        # Setting if docker is in use to false
        "use_docker": False,
    },
    # Currently never taking user input after first input
    human_input_mode="NEVER",
    # Max number of auto replies before terminating conversation.
    max_consecutive_auto_reply=2,
)

# Standard assistant agent
agent_one = autogen.AssistantAgent(
    name="MultiTalentAgent",
    llm_config=LLM_CONFIG,
)

''' In order to implement websockets - I inherit from the autogen user proxy and added the socket io emmitting
    functionality to have realtime communication of agents display to the user
'''  
class WebSocketUserProxy(autogen.UserProxyAgent):

    #*args and *kwars are used to ensure all positional and keyword arguments required for the user proxy initilisation
    def __init__(self, session_id: str ,  socketio_instance: SocketIO, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #session id used for emmiting data to the client
        self.session_id = session_id
        #THe websocket used for transfering daata
        self.socket_io = socketio_instance


    #https://microsoft.github.io/autogen/0.2/docs/reference/agentchat/conversable_agent
    #override the user proxy recieve method to add websocket emmiting functionality.
    def receive(self, message, sender, request_reply=None, silent=False):

        #Ensure the socket exists
        if self.socket_io: 
            #print for self testing and fixing of bugs 
            print(f"WebSocketUserProxy emitting to room {self.session_id}: {message}")

            # emit the message
            self.socket_io.emit('agent_message', {'content': message}, room=self.session_id)

                
        else:
            #print if there is no socket
            print(f"ERROR: WebSocketUserProxy for session {self.session_id} has no socket_io instance.")


        # Default UserProxyAgent's receive often returns (True, None) if human_input_mode is NEVER
        # Call super().receive AFTER emitting.
        return super().receive(message=message, sender=sender, request_reply=request_reply, silent=silent)


