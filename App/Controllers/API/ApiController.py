# append root path
import os, sys, uuid
sys.path.append(os.getcwd())

# import local libraries
from App.Helpers import DirectoryHelper, DatabaseHelper

# import libraries
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

import numpy as np
import pandas as pd
import joblib

def store_prediction(prediction_result, data):
    data_query = """insert into projects."broiler_prediction"."prediction_result"(id, days, temperature, humidity, amonia, food, drink, weight, population, cage_area, prediction, date_data_origin, date_created) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    data_values = (str(uuid.uuid4()), data['Hari Ke-'], data['Suhu'], data['Kelembaban'], data['Amoniak'], data['Pakan'], data['Minum'], data['Bobot'], data['Populasi'], data['Luas Kandang'], prediction_result, data['Datetime'], DatabaseHelper.get_current_timestamp())
    DatabaseHelper.perform_database_query(data_query, data_values)

def get_prediction_data():
    data_query = """select * from projects."broiler_prediction"."prediction_result";"""
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
            "date_data_origin": response_data[11], 
            "date_created": response_data[12]
        })
    
    return data

def prform_prediction(data):
    # read data as json
    dataFrame = pd.DataFrame([data])

    # process datetime data
    dataFrame['Datetime'] = pd.to_datetime(dataFrame['Datetime'])
    dataFrame['Hour'] = dataFrame['Datetime'].dt.hour

    # add session type
    dataFrame['Session'] = dataFrame['Hour'].apply(get_session_type)

    # choose the required columns
    df_X = dataFrame.drop(['Datetime','Hari Ke-'], axis=1)

    # perform encoding
    cats = df_X.select_dtypes(include=['object', 'bool']).columns
    cat_features = list(cats.values)

    le = LabelEncoder()
    for i in cat_features:
        df_X[i] = le.fit_transform(df_X[i])

    # convert value to a float
    X = df_X.astype(float).values

    # perform scaling
    scaler = StandardScaler().fit(X)
    X = scaler.transform(X)

    # load model
    model_path = DirectoryHelper.get_model_dir('rf_timestamp')
    model = joblib.load(model_path)

    # perform prediction
    result = model.predict(X)

    # store prediction to database
    store_prediction(round(result[0]), data)

    # return prediction result
    return determine_prediction_result(result[0])

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