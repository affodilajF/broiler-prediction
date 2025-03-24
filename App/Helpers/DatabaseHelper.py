# import libraries
import os
import psycopg2

from datetime import datetime
from dotenv import load_dotenv

# load env file
load_dotenv(override=True)

def connect_cockroach():
    username = os.getenv('database_user')
    password = os.getenv('database_user_password')

    db_name = os.getenv('database_name')
    db_port = os.getenv('database_port')
    db_cluster = os.getenv('database_cluster')
    
    db_url = f'postgresql://{username}:{password}@{db_cluster}:{db_port}/{db_name}?sslmode=verify-full'

    try:
        with psycopg2.connect(db_url) as conn:
            # print('Connected to the PostgreSQL server')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def connect():
    try:
        conn = psycopg2.connect(
            dbname   = os.getenv('server_db_name'),
            user     = os.getenv('server_db_user'),
            password = os.getenv('server_db_pass'),
            host     = os.getenv('server_db_host'),
            port     = os.getenv('server_db_port')
        )

        return conn

    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def perform_database_query(query, values=None):
    try:
        # connect to database
        conn = connect()
        cur = conn.cursor()

        # execute query
        if values == None:
            cur.execute(query)
            data = cur.fetchall()

            return data
            
        else:
            cur.execute(query, values)

        # Commit changes
        conn.commit()

    except Exception as e:
        conn.rollback()
        print("An error has occurred: ", e)

    finally:
        # close connection
        cur.close()
        conn.close()

def get_current_timestamp():
    current_datetime = datetime.now()
    return current_datetime.strftime("%Y-%m-%d %H:%M:%S")