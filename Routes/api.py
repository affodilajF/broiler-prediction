# append root path
import os, sys
sys.path.append(os.getcwd())

# import local libraries
from App.Controllers.API import ApiController

# get all required libraries
from flask import Blueprint, jsonify, request
from flask_cors import CORS

# initiate blueprint
api = Blueprint('api', __name__)
CORS(api, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})

@api.route('/')
def main():
    return jsonify(
        {
            'response': 'Broiler Model API is ready to accept request!',
            'status': 200,
            'messages': 'success'
        }
    )

@api.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    response = ApiController.prform_prediction(data['data'])
    return jsonify(
        {
            'response': response,
            'status': 200,
            'messages': 'success'
        }
    )

@api.route('/get_prediction_data', methods=['GET'])
def prediction_data():
    response = ApiController.get_prediction_data()
    return jsonify(
        {
            'response': response,
            'status': 200,
            'messages': 'success'
        }
    )

@api.route('/login', methods=['POST'])
def login():
    try:
        response = ''
        return jsonify(
            {
                'response': response,
                'status': 200,
                'messages': 'success'
            }
        )
    except Exception as e:
        return jsonify(
            {
                'response': str(e),
                'status': '200 OK',
                'messages': 'Something is Wrong!'
            }
        )