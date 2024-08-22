# append root path
import os, sys
sys.path.append(os.getcwd())

# import local libraries
from App.Controllers.API import ApiController

# get all required libraries
from flask import Blueprint, jsonify, request

# initiate blueprint
api = Blueprint('api', __name__)

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