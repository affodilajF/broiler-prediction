# append root path
import os, sys
sys.path.append(os.getcwd())

# import middleware
from App.Middleware import AuthMiddleware
from flask import session, render_template, redirect, url_for

# load env file
from App.Helpers.env_loader import load_environment
load_environment()

def index():
    if AuthMiddleware.check_xsrf_token():
        return render_template('Pages/Admin/index.html', base_url = os.getenv('SERVER_IP_ADDRESS'))
    
    return redirect(url_for('web.auth'))

def index_2():
    if AuthMiddleware.check_xsrf_token():
        return render_template('Pages/Admin/index_2.html', base_url = os.getenv('SERVER_IP_ADDRESS'))
    
    return redirect(url_for('web.auth'))
    