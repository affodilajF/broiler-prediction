# append root path
import os, sys, requests
sys.path.append(os.getcwd())

# import middleware
from App.Middleware import AuthMiddleware

from flask import session, render_template, redirect, url_for
from dotenv import load_dotenv

# load env file
load_dotenv(override=True)

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