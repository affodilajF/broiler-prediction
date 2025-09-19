# append root path
import os, sys

from App.Controllers.Auth import AuthController
sys.path.append(os.getcwd())

# import local libraries
from App.Controllers.API import ApiController, CageController, DailyActivityController

# get all required libraries
from flask import Blueprint, jsonify, request
from flask_cors import CORS

from App.Middleware.VerifyToken import verify_token
from App.Helpers.DBExceptionsMapper import map_db_exception, APIError, BadRequestError, ConflictError

# initiate blueprint
api = Blueprint('api', __name__)
CORS(api, supports_credentials=True)

import logging
logging.basicConfig(level=logging.INFO)   

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
     
    
# Register    
@api.route('/register', methods=['POST'])
def register():
    try:
        AuthController.register(
            firebase_id= request.json.get('firebase_id'),
            province = request.json.get('province'),
            city = request.json.get('city'),
            phone= request.json.get('phone'),
            name = request.json.get('name'),
            email    = request.json.get('email')
        )
        return jsonify({
            "response": True,
            "messages": "success"
        }), 200  
    except Exception as e:
        return jsonify({
            "response": str(e),
            "messages": "Something is Wrong!"
        }), 500  
    
    
@api.route('/add-cage', methods=['POST'])
@verify_token
def add_cage():
    firebase_id = request.user['uid']
    try:
        response = CageController.add_cage(
            firebase_id = firebase_id,
            cage_area = request.json.get('cage_area'),
            device_id = request.json.get('device_id'),
            initial_population = request.json.get('initial_population'),
        )
        return jsonify({
            "response": response,
            "messages": "success"
        }), 200  
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        return jsonify({"response": str(e), "messages": "Something is Wrong!"}), 500
    

@api.route('/get-cages', methods=['GET'])
@verify_token
def get_cages():
    try:
        firebase_id = request.user['uid']
        offset_str = request.headers.get("X-User-Offset", "+00:00")
        response = CageController.get_cage_data(firebase_id=firebase_id, offset_str=offset_str)
        logging.info(f"Offset string from header: {offset_str}")

        return jsonify({"response": response, "messages": "success"}), 200
    except Exception as e:
        return jsonify({"response": str(e), "messages": "Something is Wrong!"}), 500
    

@api.route('/activate-cage', methods=['POST'])
@verify_token
def activate_cage_endpoint():
    try:
        response = CageController.activate_cage(
            cage_id=request.json.get('cage_id'),
            date_activated_str=request.json.get('date_activated'),
            offset_str=request.headers.get("X-User-Offset", "+00:00")
        )
        return jsonify({"response": response, "messages": "success"}), 200

    except APIError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        return jsonify({"response": str(e), "messages": "Something is Wrong!"}), 500


    
    
# NOT DONE YET
@api.route('/get-daily-activities/<cage_id>', methods=['GET'])
def get_daily_activities(cage_id):
    try:
        response = DailyActivityController.get_daily_activities(cage_id=cage_id)
        return jsonify({
            "response": response,
            "messages": "success"
        }), 200  
    except Exception as e:
        return jsonify({
            "response": str(e),
            "messages": "Something is Wrong!"
        }), 500
    
@api.route('/add-daily-activity', methods=['POST'])
def add_daily_activity():
    try:
        response = DailyActivityController.add_daily_activity(
            cage_id = request.json.get('cage_id'),
            food = request.json.get('food'),
            drink = request.json.get('drink'),
            weight = request.json.get('weight'),
            death = request.json.get('death'),
            day = request.json.get('day')
        )
        return jsonify({
            "response": response,
            "messages": "success"
        }), 200  
    except Exception as e:
        return jsonify({
            "response": str(e),
            "messages": "Something is Wrong!"
        }), 500  
    

    
