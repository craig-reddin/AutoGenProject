# Code to ensure agents name provided by user does not break naming standards of agent.
# https://www.geeksforgeeks.org/python-removing-unwanted-characters-from-string/?utm_source    
import re

def refactor_agent_name(name):

    #Ensures agent names provided by users do not break naming standards 
    # Replace invalid characters with underscores
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)
