# append root path
import os, sys, uuid, requests
sys.path.append(os.getcwd())

# import local libraries
from App.Helpers import DirectoryHelper, DatabaseHelper

# import libraries
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from dotenv import load_dotenv

import numpy as np
import pandas as pd
import joblib

import numpy as np
import pandas as pd
from math import sqrt

from sklearn.model_selection import train_test_split
from scipy.stats import kurtosis, skew
from datetime import datetime
import pytz

# load env file
load_dotenv(override=True)

def store_prediction(prediction_result: int, data: dict) -> None:
    data_query = f"""insert into {os.getenv('server_db_name')}."broiler_prediction"."prediction_result"(id, days, temperature, humidity, amonia, food, drink, weight, population, cage_area, prediction, date_data_origin, date_created) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    data_values = (str(uuid.uuid4()), data['Hari Ke-'], data['Suhu'], data['Kelembaban'], data['Amoniak'], data['Pakan'], data['Minum'], data['Bobot'], data['Populasi'], data['Luas Kandang'], prediction_result, data['Datetime'], DatabaseHelper.get_current_timestamp())
    DatabaseHelper.perform_database_query(data_query, data_values)


def store_forecasting(prediction_result: int, data, date_created: datetime) -> None:
    data_query = f"""insert into {os.getenv('server_db_name')}."broiler_prediction"."forecasting_result"(id, temperature, humidity, amonia, food, drink, weight, population, cage_area, class, prediction, date_data_origin, date_created) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    data_values = (str(uuid.uuid4()), data['temp'], data['hum'], data['ammo'], data['Pakan'], data['Minum'], data['Bobot'], data['Populasi'], data['Luas Kandang'], data['Class'], prediction_result, data['datetime'], date_created)
    DatabaseHelper.perform_database_query(data_query, data_values)

def get_prediction_data():
    data_query = f"""select * from {os.getenv('server_db_name')}."broiler_prediction"."prediction_result";"""
    array_data = DatabaseHelper.perform_database_query(data_query)

    data = list()
    for response_data in array_data:
        data.append({
            "id": response_data[0], 
            "days": response_data[1], 
            "temperature": response_data[2], 
            "humidity": response_data[3], 
            "amonia": response_data[4], 
            "food": response_data[5], 
            "drink": response_data[6], 
            "weight": response_data[7], 
            "population": response_data[8], 
            "cage_area": response_data[9], 
            "prediction": response_data[10], 
            "date_data_origin": str(response_data[11]), 
            "date_created": str(response_data[12])
        })
    
    return data

def get_forecasting_data():
    data_query = f"""select * from {os.getenv('server_db_name')}."broiler_prediction"."forecasting_result";"""
    array_data = DatabaseHelper.perform_database_query(data_query)

    data = list()
    for response_data in array_data:
        data.append({
            "id": response_data[0],  
            "temperature": response_data[1], 
            "humidity": response_data[2], 
            "amonia": response_data[3], 
            "food": response_data[4], 
            "drink": response_data[5], 
            "weight": response_data[6], 
            "population": response_data[7], 
            "cage_area": response_data[8], 
            "class": response_data[9],
            "prediction": response_data[10], 
            "date_data_origin": str(response_data[11]), 
            "date_created": str(response_data[12]) 
        })
    
    return data

def perform_prediction(data):
    # read data as json
    dataFrame = pd.DataFrame([data])

    # process datetime data
    dataFrame['Datetime'] = pd.to_datetime(dataFrame['Datetime'])
    dataFrame['Hour'] = dataFrame['Datetime'].dt.hour

    # add session type
    dataFrame['Session'] = dataFrame['Hour'].apply(get_session_type)

    # choose the required columns
    df_X = dataFrame.drop(['Datetime','Hari Ke-','Death'], axis=1)

    # convert value to a float
    X = df_X.astype(float).values

    # load model
    model_path = DirectoryHelper.get_model_dir('rf_timestamp')
    model = joblib.load(model_path)

    # perform prediction
    result = model.predict(X)

    # store prediction to database
    store_prediction(round(result[0]), data)

    # return prediction result
    return determine_prediction_result(result[0])

def perform_forecasting(data):
    # read data as json
    dataFrame = pd.DataFrame.from_dict(data)

    # process datetime data
    dataFrame['datetime'] = pd.to_datetime(dataFrame['datetime'])
    dataFrame['Hour'] = dataFrame['datetime'].dt.hour

    # choose the required columns
    df_X = dataFrame[['temp','hum','ammo','Death','Death']]
    in_seq = df_X.astype(float).values

    n_steps_in, n_steps_out = 6, 0
    X, y = get_sequences(in_seq, n_steps_in, n_steps_out)

    n_input = X.shape[1] * X.shape[2]
    X = X.reshape((X.shape[0], n_input))
    X = get_stats_features(X)

    # load model
    model_path = DirectoryHelper.get_model_dir('mlp_timestamp_forecasting')
    model = joblib.load(model_path)

    # perform prediction
    result = model.predict(X)

    # store prediction to database
    curr_date = DatabaseHelper.get_current_timestamp()
    for i in data:
        store_forecasting(round(result[0]), i, curr_date)

    # return prediction result
    return round(result[0])

def get_session_type(hour):
    if (hour > 4) and (hour <= 8):
        return 0 #'Early morning'
    elif (hour > 8) and (hour <= 12 ):
        return 1 #'Morning'
    elif (hour > 12) and (hour <= 16):
        return 2 #'Noon'
    elif (hour > 16) and (hour <= 20):
        return 3 #'Eve'
    elif (hour > 20) and (hour <= 24):
        return 4 #'Night'
    elif (hour <= 4):
        return 5 #'Late Night'
    
def determine_prediction_result(prediction):
    if int(prediction) == 0:
        return 'normal'
    elif int(prediction) == 1:
        return 'abnormal'
    else:
        return 'cannot predict'

def get_stats_features(input_data):
    inp = list()
    for i in range(len(input_data)):
        inp2 = list()
        inp2 = input_data[i]
        min  = float(np.min(inp2))
        max  = float(np.max(inp2))
        diff = (max-min)
        std  = float(np.std(inp2))
        mean = float(np.mean(inp2))
        median = float(np.median(inp2))
        kurt = float(kurtosis(inp2))
        sk   = float(skew(inp2))
        inp2 = np.append(inp2,min)
        inp2 = np.append(inp2,max)
        inp2 = np.append(inp2,diff)
        inp2 = np.append(inp2,std)
        inp2 = np.append(inp2,mean)
        inp2 = np.append(inp2,median)
        inp2 = np.append(inp2,kurt)
        inp2 = np.append(inp2,sk)
        inp  = np.append(inp,inp2)

    inp = inp.reshape(len(input_data),-1)

    return inp

def get_sequences(sequences, n_steps_in, n_steps_out):
	X, y = list(), list()
	for i in range(len(sequences)):
		end_ix = i + n_steps_in
		out_end_ix = end_ix + n_steps_out
		if out_end_ix > len(sequences):
			break

		seq_x, seq_y = sequences[i:end_ix, :-1], sequences[out_end_ix - 1, -1]
		X.append(seq_x)
		y.append(seq_y)

	return np.array(X), np.array(y)

def get_xsrf_token():
    request = requests.get(f'{os.getenv("server_external_api_ip_address")}/csrf-cookie')

    if request.status_code == 200:
        return {
            'status': '200 OK',
            'massage': 'Success',
            'response': request.cookies.get('XSRF-TOKEN')
        }
    else:
        return {
            'status': request.status_code,
            'massage': 'Semething is wrong!',
            'response': ''
        }