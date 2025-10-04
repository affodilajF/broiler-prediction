import os
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, auth
from App.Middleware.VerifyToken import verify_token


# import helper
from App.Helpers import DirectoryHelper

# import routes
from Routes import web as web_routes, api as api_routes

# import config
from config import DevelopmentConfig, ProductionConfig

from App.Helpers.env_loader import load_environment

load_environment()

# initiate flask app
working_dir = DirectoryHelper.get_curr_work_dir()
app = Flask(
    __name__,
    template_folder=working_dir['templates_dir'],
    static_url_path='',
    static_folder=working_dir['public_dir']
)

# pilih config sesuai env
APP_ENV = os.getenv("APP_ENV", "development")
if APP_ENV == "production":
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# ---------------------
# Firebase Admin init
# ---------------------

cred_path = os.getenv("FIREBASE_CRED", "firebase-credentials.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


# ---------------------
# MQTT
# ---------------------
from Mqtt.MqttClient import mqtt_client
mqtt_client.init_app(app=True)
mqtt_client.subscribe(os.getenv('IOT_MQTT_TOPIC', 'iot/broiler/#'))

# ---------------------
# Register blueprints
# ---------------------

app.register_blueprint(api_routes.api, url_prefix='/api')
app.register_blueprint(web_routes.web, url_prefix='/')


# ---------------------
# Run flask application
# ---------------------

if __name__ == '__main__':
    print(f"Flask running in {APP_ENV} mode, debug={app.config['DEBUG']}")
    app.run(host='0.0.0.0', debug=app.config['DEBUG'])
