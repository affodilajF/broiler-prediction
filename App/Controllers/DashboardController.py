# append root path
import os, sys
sys.path.append(os.getcwd())

# import middleware
from App.Middleware import AuthMiddleware

from dotenv import load_dotenv
from flask import session, render_template, redirect, url_for

# load env file
load_dotenv(override=True)

def index():
    if AuthMiddleware.check_xsrf_token():
        return render_template('Pages/Admin/index.html', base_url = os.getenv('server_ip_address'))
    
    return redirect(url_for('web.auth'))
    