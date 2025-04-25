from flask import Blueprint, request, jsonify
from db_connection import connect_to_database

team_blueprint = Blueprint('team', __name__)

#POST endpoint to store the chats completed 
@team_blueprint.route('/store_team', methods=['POST'])
def store_team():
    try:
        #extract the payload data
        data = request.json
        teamName = data['teamName']
        userEmail = data['userEmail']
        teamDescription = data['teamDescription']
        agentOne = data['agentOne']
        agentTwo = data['agentTwo']
        agentThree = data['agentThree']
        
        conn = connect_to_database()        
        cursor = conn.cursor()
        #execute the query with inserted variables
        cursor.execute(
            "INSERT INTO agentteams (useremail, teamname, teamdescription, teamagentone, teamagenttwo, teamagentthree) VALUES (%s, %s, %s, %s, %s, %s)",
            (userEmail, teamName, teamDescription, agentOne, agentTwo, agentThree)
        )
        #commit transaction, close cursor and close connection
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"response": "Team stored"}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

#POST endpoint to get all the teams belonging to a user of a particulary email address
@team_blueprint.route('/gather_teams', methods=['POST'])
def gather_teams():
    try:
        data = request.json
        email = data['email']

        if isinstance(email, str):
            conn = connect_to_database()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT teamname, teamdescription, teamagentone, teamagenttwo, teamagentthree FROM agentteams WHERE useremail = %s", 
                (email,)
            )

            #Get all agent teams
            result = cursor.fetchall()
            #format for easy extraction on frontend
            formatted_result = [[[teamname], [teamdescription], [teamagentone], [teamagenttwo], [teamagentthree]] 
                               for teamname, teamdescription, teamagentone, teamagenttwo, teamagentthree in result]

            
            if not result:
                chat_content = "<div id='previous_chat_error'><h1 id='returned_data'>Error fetching chat data</h1><br /><h3 id='previous_chat_error_sub'>Please try again later</h3></div>"  
                return jsonify({"message": chat_content}), 200
                
            cursor.close()
            conn.close()
        
        return jsonify({"message": formatted_result}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500
