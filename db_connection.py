import psycopg2
from config import DATABASE_NAME, DATABASE_HOST, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_PORT

def connect_to_database():
    # Connect to database using the environment variables
    conn = psycopg2.connect(
        database=DATABASE_NAME,
        host=DATABASE_HOST,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        port=DATABASE_PORT
    )
    
    # Return the connection
    return conn
