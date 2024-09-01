# append root path
import os, sys
sys.path.append(os.getcwd())

# import controllers
from App.Controllers.Auth import AuthController
from App.Controllers import DashboardController

# import flask
from flask import Blueprint, request

# initiate blueprint
web = Blueprint('web', __name__)

# routes
@web.route('/')
def index(): 
    return AuthController.index()

@web.route('/dashboard')
def dashboard():
    return DashboardController.index()

@web.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        AuthController.authenticate_user(request.form.get('email'), request.form.get('password'))

    return AuthController.index()


    