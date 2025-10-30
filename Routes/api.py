# append root path
import os, sys

from App.Controllers.Auth import AuthController
sys.path.append(os.getcwd())

# import local libraries
from App.Controllers.API import ApiController, CageController, DailyActivityController, IoTController, NotificationController, AIoTTestingController
# from App.Controllers.API import ApiController, CageController, DailyActivityController

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
    
@api.route('/get-profile', methods=['GET'])
@verify_token
def get_user_profile():
    try:
        firebase_id = request.user['uid']
        offset_str = request.headers.get("X-User-Offset", "+00:00")
        response = AuthController.get_user_profile(firebase_id, offset_str)

        return jsonify({"response": response, "messages": "success"}), 200
    except Exception as e:
        return jsonify({"response": str(e), "messages": "Something is Wrong!"}), 500    
    
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
            cage_name= request.json.get('cage_name')
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


@api.route('/get-cages-v2', methods=['GET'])
@verify_token
def get_cages_v2():
    try:
        firebase_id = request.user['uid']
        offset_str = request.headers.get("X-User-Offset", "+00:00")
        response = CageController.get_cage_data_v2(firebase_id=firebase_id, offset_str=offset_str)
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
    
@api.route('/get-daily-activities/<cage_id>', methods=['GET'])
@verify_token
def get_daily_activities(cage_id):
    try:
        response = DailyActivityController.get_daily_activities(
            cage_id=cage_id,
            offset_str=request.headers.get("X-User-Offset", "+00:00")
        )
        return jsonify({
            "response": response,
            "messages": "success"
        }), 200  
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        return jsonify({"response": str(e), "messages": "Something is Wrong!"}), 500
    
@api.route('/add-daily-activity', methods=['POST'])
@verify_token
def add_daily_activity():
    try:
        response = DailyActivityController.add_daily_activity(
            cage_id = request.json.get('cage_id'),
            dailyactivity_date= request.json.get('date'),
            food = request.json.get('food'),
            drink = request.json.get('drink'),
            weight = request.json.get('weight'),
            death = request.json.get('death'),
            offset_str=request.headers.get("X-User-Offset", "+00:00"),
            notes= request.json.get('notes')
        )
        return jsonify({
            "response": response,
            "messages": "success"
        }), 200  
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        return jsonify({"response": str(e), "messages": "Something is Wrong!"}), 500
    
@api.route('/get-notif-history', methods=['GET'])
@verify_token
def get_notif_history():
    try:
        firebase_id = request.user['uid']
        response = NotificationController.get_notification_history(
            firebase_id=firebase_id,
            offset_str=request.headers.get("X-User-Offset", "+00:00")
        )
        return jsonify({
            "response": response,
            "messages": "success"
        }), 200  
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        return jsonify({"response": str(e), "messages": "Something is Wrong!"}), 500
    
@api.route('/update-read-status-notifications', methods=['POST'])
@verify_token
def update_read_status_notifications():
    try:
        notification_ids = request.json.get('notification_ids', [])
        response = NotificationController.update_notification_status(
            notification_ids=notification_ids
        )
        return jsonify({
            "response": response,
            "messages": "success"
        }), 200  
    except APIError as e:
        return jsonify(e.to_dict()), e.status_code

    except Exception as e:
        return jsonify({"response": str(e), "messages": "Something is Wrong!"}), 500
    
@api.route('/check-model-pred', methods=['POST'])
def check_model():
    try:
        suhu = float(request.json.get('suhu'))
        kelembaban = float(request.json.get('kelembaban'))
        amoniak = float(request.json.get('amoniak'))
        unix_ts = int(request.json.get('unix_ts'))

        result = IoTController.perform_prediction(suhu, kelembaban, amoniak, unix_ts)

        return jsonify({
            'status': 'success',
            'prediction': result
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    

# Testing endpoint to run model immediately (normal prediction)
@api.route('/run-model-now', methods=['GET'])
def run_model_now():
    try:
        result = AIoTTestingController.perform_prediction_and_store(
            offset_str=request.headers.get("X-User-Offset", "+00:00"),
            testing_is_normal_prediction=True
        )

        return jsonify({
            'status': 'success',
            'message': 'Model run successfully' if result else 'Model run failed'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    

# Testing endpoint to run model immediately (abnormal prediction)
@api.route('/run-model-now-abnormal', methods=['GET'])
def run_model_now_abnormal():
    try:
        result = AIoTTestingController.perform_prediction_and_store(
            offset_str=request.headers.get("X-User-Offset", "+00:00"),
            testing_is_normal_prediction=False
        )

        return jsonify({
            'status': 'success',
            'message': 'Model run successfully' if result else 'Model run failed'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

