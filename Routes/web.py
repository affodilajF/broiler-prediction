from flask import Blueprint, render_template
web = Blueprint('web', __name__)

@web.route('/')
def main():
    return render_template('Pages/Admin/index.html')