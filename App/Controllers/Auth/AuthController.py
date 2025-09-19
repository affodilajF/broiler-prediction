# append root path
import os, sys, requests
from datetime import datetime
sys.path.append(os.getcwd())
from App.Middleware import AuthMiddleware

from flask import session, render_template, redirect, url_for
from App.Helpers import DirectoryHelper, DatabaseHelper
from App.Helpers.env_loader import load_environment
load_environment()


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
