from flask import Blueprint, request, jsonify
from db_connection import connect_to_database

agent_blueprint = Blueprint('agent', __name__)

@agent_blueprint.route('/create_agent', methods=['POST'])
def create_agent():
    try:
        # Retrieve JSON data from the body
        data = request.json
        #Extract email from payload
        email = data["email"]
        #Extract specialistation from payload
        specialisation = data.get('specialisation')
        #Extract prompt from payload
        prompt = data.get('prompt')

        #call connect_to_database - get database connection
        conn = connect_to_database()
        # create curor obrct for sending query
        cursor = conn.cursor()
        #execute the query
        cursor.execute(
            "INSERT INTO agentdata (useremail, agentspecialisation, agentconfig, temperature, userintervention) VALUES (%s, %s, %s, %s, %s)",
            (email, specialisation, prompt, 0.0, False)
        )
        
        #commit transaction
        conn.commit()
        #close the curson
        cursor.close()
        #close the database connection
        conn.close()
        
        result = "Agent Created"
        #Return the message
        return jsonify({"message": result}), 200
    except Exception as e:
        #return the error if one occurs
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@agent_blueprint.route('/retrieve_agents', methods=['POST'])
def retrieve_agents():
    try:
        data = request.json
        #Extract email from payload
        email = data['email']
        
        conn = connect_to_database()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT agentspecialisation, agentconfig, agentid FROM agentdata WHERE useremail = %s OR useremail = 'system@example.com'", 
            (email,)
        )
        #fetch all used for gathering all agents associated with the passed email
        result = cursor.fetchall()
        #format the result for extraction on the client side
        #https://www.geeksforgeeks.org/nested-list-comprehensions-in-python/
        formatted_result = [[[agentspecialisation], [agentconfig], [agentid]] for agentspecialisation, agentconfig, agentid in result]

        #   if the no result retrun - return html content (stlyed when rendered in) - Understood this is dangerous now since learning of xss in secure app dev
        # Dont have enough time to refactor sections that implemented this. 
        if not result:
            chat_content = "<div id='previous_chat_error'><h1 id='returned_data'>Could not fetch agent</h1><br /><h3 id='previous_chat_error_sub'>Please try again later</h3></div>"  
            return jsonify({"message": chat_content}), 200
            
        cursor.close()
        conn.close()
        
        return jsonify({"message": formatted_result}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500
