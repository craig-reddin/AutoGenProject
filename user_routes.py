from flask import Blueprint, request, jsonify
from db_connection import connect_to_database

user_blueprint = Blueprint('user', __name__)

#POST Endpoint to verify a users credentials - currently no implemented into application as Auth0 was utilised for user authentication
@user_blueprint.route('/sign_in_user', methods=['POST'])
def sign_in_user():
    try:
        data = request.json
        
        userEmail = data["emailAddress"]
        userPassword = data["password"]  
        
        conn = connect_to_database()
        cursor = conn.cursor()

        query = "SELECT useremail, userpassword FROM usertable WHERE useremail = %s"
        cursor.execute(query, (userEmail,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()
         
        if result:
            email, password = result 
            if email == userEmail and password == userPassword:
                response_message = "Sign in was successful"
            else:
                response_message = "Incorrect credentials"
        else:
            response_message = "User not found"

        #return the appropriate message depending on the outcome of the transaction and value comparison
        return jsonify({"response": response_message}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"response": "An error occurred", "details": str(e)}), 500
# API endpoint called after the user signs in using Auth0
#Verify the email exists and if it does not, save the new user of the app to the database
@user_blueprint.route('/review_sign_in', methods=['POST'])
def review_sign_in():
    try:
        #extract the payload data
        data = request.json
        name = data["name"]
        email = data["email"]
        #connect to database and cursor
        conn = connect_to_database()        
        cursor = conn.cursor()
        new_user = False

        #execute transaction
        query = "SELECT useremail FROM usertable WHERE useremail = %s"
        cursor.execute(query, (email,))
        #get one single record
        result = cursor.fetchone()
        if result is None:
            #if ther email is not found call the create_user method and save the new user to the database.
            create_user(email, name)
            new_user = True
            
        #commit transaction
        conn.commit()
        #close cursor
        cursor.close()
        #close connection
        conn.close()
        
        if(new_user):    
            return jsonify({"response": "User Created"}), 200
        return jsonify({"response": "User Existed"}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


#Endpoint to delete user from the system
@user_blueprint.route('/delete_user', methods=['POST'])
def delete_user_route():
    try:
        #extract the email from the payload
        data = request.json
        userEmail = data['email']
        
        deletion_result = delete_user_flow(userEmail)
        #call delete_user_flow and pass the email
        #if all methods ran successfully the below message will be returned
        if deletion_result:
            response = "User Deleted"
            #return the response
            return jsonify({"response": response}), 200

        #Return the user was not deleted response
        response = "User Not Deleted"
        return jsonify({"response": response}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

#Method to create a new user - called when verifying users sign in email - if the email is not stored in the database
def create_user(email, name):
    try:   
        conn = connect_to_database()        
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO usertable (useremail, UserFirstName) VALUES (%s, %s)",
            (email, name)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

#Method to call methods to delete a users chats, teams, agents and then the user themself from the database
def delete_user_flow(email):
    # Call each delete method and store the result
    chat_result = delete_chats(email)
    team_result = delete_teams(email)
    agent_result = delete_agents(email)
    user_result = delete_user(email)

    # These comparisons could be changed to booleans
    #If I have time to refactor before submission I will
    #Dont know what I was thinking :)
    
    if (chat_result and 
        team_result and 
        agent_result and 
        user_result ):
        return "All Deletions Successful"
    else:
        return "Deletion Failed"

#function called to delete a users chats
def delete_chats(email):
    print("hello chats")
    try:
        conn = connect_to_database()        
        cursor = conn.cursor() 
        query = "DELETE FROM chattable WHERE useremail = %s"
        cursor.execute(query, (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:       
        return False

#function called to delete all of a users teams stored
def delete_teams(email):
    print("hello teams")
    try:
        conn = connect_to_database()        
        cursor = conn.cursor() 
        query = "DELETE FROM agentteams WHERE useremail = %s"
        cursor.execute(query, (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return False    

#a method to delete a users agents
def delete_agents(email):
    print("hello agents")
    try:
        conn = connect_to_database()        
        cursor = conn.cursor() 
        query = "DELETE FROM agentdata WHERE useremail = %s"
        cursor.execute(query, (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return False
#A method used to delete the users account - the user will still have an Auth0 account after deleting their information from the GenAIColab Application
def delete_user(email):
    print("hello user")
    try:
        conn = connect_to_database()        
        cursor = conn.cursor() 
        query = "DELETE FROM usertable WHERE useremail = %s"
        cursor.execute(query, (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return False
