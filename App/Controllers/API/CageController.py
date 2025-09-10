
import os, sys, uuid, requests

from App.Helpers import DatabaseHelper
from datetime import datetime
sys.path.append(os.getcwd())

import logging
logging.basicConfig(level=logging.INFO)  


def add_cage(user_id, initial_population, cage_area):
    cage_id = str(uuid.uuid4())
    status = 'non-active'  
    date_activated = None

    data_query = f"""
        insert into {os.getenv('DATABASE_NAME')}."broiler_app"."cages"
        (id, user_id, initial_population, current_population, cage_area, status, date_activated)
        values (%s, %s, %s, %s, %s, %s);
    """
    data_values = (cage_id, user_id, initial_population, initial_population, cage_area, status, date_activated)
    DatabaseHelper.perform_database_query(data_query, data_values)

    return True


def activate_cage(cage_id):
    status = 'active'
    date_activated = datetime.now() 

    data_query = f"""
        update {os.getenv('DATABASE_NAME')}."broiler_app"."cages"
        set status = %s,
            date_activated = %s
        where id = %s;
    """
    data_values = (status, date_activated, cage_id)
    DatabaseHelper.perform_database_query(data_query, data_values)

    return True

def get_cage_data(user_id):
    data_query = f"""select * from {os.getenv('DATABASE_NAME')}."broiler_app"."cages" where user_id = %s;"""
    array_data = DatabaseHelper.perform_database_query_v2(data_query, (user_id,)) or []

    logging.info(f"Running query: {data_query} with params: {user_id}")
    logging.info(f"Query result: {array_data}")
    return [
        {
            "id": row[0],
            "initial_population": row[2],
            "current_population": row[3],
            "cage_area": row[4],
            "status": row[5],
            "date_activated": str(row[6])
        }
        for row in array_data
    ]


