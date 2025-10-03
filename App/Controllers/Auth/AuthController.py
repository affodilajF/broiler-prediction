# append root path
import os, sys, requests
from datetime import datetime
sys.path.append(os.getcwd())
from App.Middleware import AuthMiddleware

from flask import session, render_template, redirect, url_for
from App.Helpers import DirectoryHelper, DatabaseHelper
from App.Helpers.env_loader import load_environment
load_environment()
from App.Helpers.DateHelper import utc_to_offset_iso


def index():
    session['base_url_api'] = os.getenv('server_ip_address')

    if AuthMiddleware.check_xsrf_token():
        return redirect(url_for('web.dashboard'))
    
    return render_template('Pages/Authentication/index.html')

def index_2():
    session['base_url_api'] = os.getenv('server_ip_address')

    if AuthMiddleware.check_xsrf_token():
        return redirect(url_for('web.forecasting'))
    
    return render_template('Pages/Authentication/index.html')

def authenticate_user(email, password):
    authenticate = requests.post(f'{os.getenv("server_external_api_ip_address")}/login', json={'email': email, 'password': password})
    if authenticate.status_code == 200:
        return True
    
    return False

# register user to database based on firebase_id
def register(firebase_id, name, province, city, phone, email):
    data_query = f"""
        INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."users"
        (firebase_id, name, province, city, phone, email, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    data_values = (
        firebase_id,
        name,
        province,
        city,
        phone,
        email,
        datetime.now()
    )

    DatabaseHelper.perform_database_query(data_query, data_values)
    return True

def get_user_profile(firebase_id, offset_str):

    data_query = f"""
        SELECT firebase_id, name, province, city, phone, email, created_at
        FROM {os.getenv('DATABASE_NAME')}."broiler_app"."users"
        WHERE firebase_id = %s
        LIMIT 1;
    """
    array_data = DatabaseHelper.perform_database_query_v2(data_query, (firebase_id,))
    return [
        {
            "id": row[0],
            "name": row[1],
            "province": row[2],
            "city": row[3],
            "phone": row[4],
            "email": row[5],
            "created_at": utc_to_offset_iso(row[6], offset_str) if row[6] else None,
        }
        for row in array_data
    ]


