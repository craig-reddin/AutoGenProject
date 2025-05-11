from flask import Blueprint, request, jsonify
from db_connection import connect_to_database
from agents import user_proxy, agent_one
from utils import refactor_agent_name
import autogen
from config import LLM_CONFIG


chat_blueprint = Blueprint('chat', __name__)

@chat_blueprint.route('/chat', methods=['POST'])
def chat():
    try:
        # Debugging log for incoming request
        print("Received POST request")
        data = request.json
        message = data['message']

        #call initialte chat pass the message and agent_one.
        user_proxy.initiate_chat(agent_one, message=message)
        
        
        # Extract and print only the content of the messages
        # Initialise an empty list to store message contents
        message_contents = []
        # Loop through user_proxy messages - user_proxy.chat_messages.items()
        for role, messages in user_proxy.chat_messages.items():
            for message in messages:
                print(message)
                # Add the message to the array
                if(message['content'] != ""):
                    message_contents.append(f"{message['name']}\n{message['content']}")
                    print("-" * 50)
            # To separate messages for appearance in the console
            
        user_proxy.chat_messages.clear()

        # Return the response and 200 success
        return jsonify({"response": message_contents}), 200
    except Exception as e:
        # Print the exception for details
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@chat_blueprint.route('/chat_team', methods=['POST'])
def chat_team():
    try:
        # Debugging log for incoming request
        print("Received POST request")
        #extract request data
        data = request.json
        message = data['message']
        agentOne = data['agentOne']
        agentTwo = data['agentTwo']
        agentThree = data['agentThree']
        
        # Database connection
        conn = connect_to_database()
        cursor = conn.cursor()

        # The agents data is extracted from the database to configure the agents.
        query = "SELECT agentspecialisation, agentconfig FROM agentdata WHERE agentid IN (%s, %s, %s)"
        cursor.execute(query, (agentOne, agentTwo, agentThree))

        # Fetch all results
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        print(result)

        stopping_termination_message = "You must NOT respond with 'TERMINATE' in any part of your rseonse.  ."
        # Unpack the results
        (specialisationOne, configurationOne), (specialisationTwo, configurationTwo), (specialisationThree, configurationThree) = result
        
        # Refactor agent names for configuration
        specialisationOne = refactor_agent_name(specialisationOne)
        specialisationTwo = refactor_agent_name(specialisationTwo)
        specialisationThree = refactor_agent_name(specialisationThree)

        # Agents and configurations, extracted from the database
        agent_one = autogen.AssistantAgent(
            name=specialisationOne,
            description=specialisationOne,
            system_message= configurationOne + " " + stopping_termination_message,
            llm_config=LLM_CONFIG,
        )
        
        agent_two = autogen.AssistantAgent(
            name=specialisationTwo,
            description=specialisationTwo,
            system_message= configurationTwo + " " + stopping_termination_message,
            llm_config=LLM_CONFIG,
        )

        agent_three = autogen.AssistantAgent(
            name=specialisationThree,
            description= specialisationThree,
            system_message= configurationThree + " " + stopping_termination_message,
            llm_config=LLM_CONFIG,   
        )
        
        # Implement the group chat
        groupchat = autogen.GroupChat(
            #pass the agents and user proxy
            agents=[user_proxy, agent_one, agent_two, agent_three], 
            #empty array to add messages
            messages=[], 
            #give a max number of interactions ensure the communication does not run possible 
            #infinitely or costing too much money for a single question when testing. 
            max_round=20
        )
        
        # Group chat manager - used to control the conversation, manages agents and decides what agent is next to speak.
        manager = autogen.GroupChatManager(
            #pass the groupchat object
            groupchat=groupchat,
            #A prompt to ensure the chat manager passes inititial message to hardcoded chat coordinatior agent.
            system_message= '''You control the flow of the chat. When the user_proxy executes code and receives an error:
            1. Always forward the error to the programming agent
            2. Explicitly ask the programming agent to fix the code
            3. After the programming agent provides a fix, direct the user_proxy to execute the updated code
            4. Repeat this cycle until the code executes successfully
            5. Only TERMINATE the conversation when all requirements are met and all code executes without errors
            Do NOT allow conversation to end while there are unresolved errors.''',
            #pass configurations, tempt, openai key and model used
            llm_config=LLM_CONFIG
        )
        
        # Initiate the chat
        user_proxy.initiate_chat(manager, message=message)
        
        #Extract message contents and append them to the message_contents array
        message_contents = []
        for role, messages in user_proxy.chat_messages.items():
            for message in messages:
                if(message['content'] != ""):
                        message_contents.append(f"{message['name']}\n{message['content']}")
                        print("-" * 50)
        #clear the chat
        user_proxy.chat_messages.clear()
        #return the entire chat content
        return jsonify({"response": message_contents}), 200
    except Exception as e:
        #if an error occurs return the error
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@chat_blueprint.route('/get_previous_chat', methods=['POST'])
def get_previous_chat():
    try:
        data = request.json
        #extract he payload chatname
        chat_name = data.get('chatName')

        print(chat_name)
        conn = connect_to_database()
        cursor = conn.cursor()
        query = "SELECT chatcontent FROM chattable WHERE chatid = %s"
        cursor.execute(query, (chat_name,))
        result = cursor.fetchone()            
        print(result)
            
        if result:
            chat_content = result[0]
        else:
            chat_content = "<div id='previous_chat_error'><h1 id='returned_data'>Error fetching chat data</h1><br /><h3 id='previous_chat_error_sub'>Please try again later</h3></div>"
            
        cursor.close()
        conn.close()
        
        return jsonify({"message": chat_content}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@chat_blueprint.route('/gather_previous_chat_names', methods=['POST'])
def gather_previous_chat_names():
    try:
        data = request.json
        email = data["email"]
        conn = connect_to_database()
        cursor = conn.cursor()
        query = "SELECT chatname, chatid FROM chattable WHERE useremail = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchall()
        print(result)
        formatted_result = [[[chatname], [chatid]] 
                               for chatname, chatid in result]
        cursor.close()
        conn.close()
        return jsonify({"message": formatted_result}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@chat_blueprint.route('/store_chat', methods=['POST'])
def store_chat():
    try:
        #Extract the payloads data
        data = request.json
        message = data['message']
        email = data["email"]
        chat_name = data["chat_name"]
        conn = connect_to_database()        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chattable (useremail, chatname, chatcontent) VALUES (%s, %s, %s)",
            (email, chat_name, message)
        )
        conn.commit()
        cursor.close()
        conn.close()
        #return 200 and Message stored
        return jsonify({"response": "Message stored"}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

#Delete Chat endpoin
@chat_blueprint.route('/delete_chat', methods=['POST'])
def delete_chat():
    try:
        #extract the data
        data = request.json
        email = data['email']
        chat_name = data['chatName']
        
        conn = connect_to_database()        
        cursor = conn.cursor() 
        query = "DELETE FROM chattable WHERE useremail = %s AND chatname = %s"
        cursor.execute(query, (email, chat_name))
        conn.commit()
        cursor.close()
        conn.close()
        #return 200 and Chat Delete message
        return jsonify({"response": "Chat Deleted"}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500
