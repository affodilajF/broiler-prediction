# import libraries
import os
import psycopg2

from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO)

from App.Helpers.env_loader import load_environment
load_environment()


def connect_cockroach():
    username = os.getenv('database_user')
    password = os.getenv('database_user_password')

    db_name = os.getenv('database_name')
    db_port = os.getenv('database_port')
    db_cluster = os.getenv('database_cluster')
    
    db_url = f'postgresql://{username}:{password}@{db_cluster}:{db_port}/{db_name}?sslmode=verify-full'
    # db_url = f"postgresql://{username}:{password}@{db_cluster}:{db_port}/{db_name}?sslmode=verify-full&sslrootcert={os.getenv('sslrootcert')}"

    try:
        with psycopg2.connect(db_url) as conn:
            print('Connected to the PostgreSQL server')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

        # conn = psycopg2.connect(
        #     dbname   = os.getenv('server_db_name'),
        #     user     = os.getenv('server_db_user'),
        #     password = os.getenv('server_db_pass'),
        #     host     = os.getenv('server_db_host'),
        #     port     = os.getenv('server_db_port')
        # )

def connect():
    logging.info("Connecting to the database...")
    try:
        username = os.getenv('DATABASE_USER')
        password = os.getenv('DATABASE_USER_PASSWORD', '')
        db_name = os.getenv('DATABASE_NAME')
        db_port = os.getenv('DATABASE_PORT')
        db_host = os.getenv('DATABASE_HOST')

        # URL koneksi CockroachDB insecure
        db_url = f'postgresql://{username}:{password}@{db_host}:{db_port}/{db_name}?sslmode=disable'

        conn = psycopg2.connect(db_url)
        logging.info("Connected to the database")
        return conn

    except (psycopg2.DatabaseError, Exception) as error:
        logging.error(f"Database connection error: {error}")
        return None

# def perform_database_query(query, values=None):
#     try:
#         # connect to database
#         conn = connect()
#         cur = conn.cursor()

#         # execute query
#         if values == None:
#             cur.execute(query)
#             data = cur.fetchall()

#             return data
            
#         else:
#             cur.execute(query, values)

#         # Commit changes
#         conn.commit()

#     except Exception as e:
#         logging.info("3 Perform : exception ...")
#         logging.info(e)
#         conn.rollback()
#         print("An error has occurred: ", e)

def perform_database_query(query, values=None):
    conn = None
    cur = None
    try:
        # connect to database
        conn = connect()
        cur = conn.cursor()

        # execute query
        if values is None:
            cur.execute(query)
            data = cur.fetchall()
            return data
        else:
            cur.execute(query, values)

        # Commit changes
        conn.commit()

    except Exception as e:
        logging.error("Perform: exception ...")
        logging.error(e)

        if conn:
            conn.rollback()

        # lempar lagi biar ketangkap di level atas (Flask route)
        raise

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def perform_database_query_v2(query, values=None):
    conn = None
    cur = None
    try:
        # connect to database
        conn = connect()
        cur = conn.cursor()

        # execute query
        if values is None:
            cur.execute(query)
        else:
            cur.execute(query, values)

        # Cek apakah query SELECT atau bukan
        if query.strip().lower().startswith("select"):
            data = cur.fetchall()
            return data
        else:
            conn.commit()
            return None

    except Exception as e:
        logging.error("Perform: exception ...")
        logging.error(e)

        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_current_timestamp():
    current_datetime = datetime.now()
    return current_datetime.strftime("%Y-%m-%d %H:%M:%S")