# import libraries
import os

from dotenv import load_dotenv
from flask import Blueprint, render_template

# load env file
load_dotenv()

# initiate blueprint
web = Blueprint('web', __name__)

# routes
@web.route('/')
def main():
    return render_template('Pages/Admin/index.html', base_url_api=os.getenv('server_ip_address'))