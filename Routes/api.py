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
CORS(api, supports_credentials=True)

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
    try:
        data = request.get_json()
        response = ApiController.perform_prediction(data['data'])
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
                'status': 500,
                'messages': 'Something is Wrong!'
            }
        )

@api.route('/forecast', methods=['POST'])
def forecast():
    try:
        data = request.get_json()
        response = ApiController.perform_forecasting(data['data'])
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
                'status': 500,
                'messages': 'Something is Wrong!'
            }
        )

@api.route('/get_prediction_data', methods=['GET'])
def prediction_data():
    try:
        response = ApiController.get_prediction_data()
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
                'status': 500,
                'messages': 'Something is Wrong!'
            }
        )

@api.route('/get_forecasting_data', methods=['GET'])
def forecasting_data():
    try:
        response = ApiController.get_forecasting_data()
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
                'status': 500,
                'messages': 'Something is Wrong!'
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
                'status': 500,
                'messages': 'Something is Wrong!'
            }
        )