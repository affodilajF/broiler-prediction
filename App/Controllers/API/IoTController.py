
import datetime
import json
import os, sys, uuid, requests

from App.Helpers import DatabaseHelper
from App.Helpers.DateHelper import get_today_range_for_wib, get_today_range_utc, get_today_utc, utc_to_offset_iso, offset_to_utc, local_to_offset_iso, now_with_offset_iso_dt
from App.Helpers.DBExceptionsMapper import map_db_exception, BadRequestError
from datetime import datetime, timezone
sys.path.append(os.getcwd())

from App.Helpers import DirectoryHelper, DatabaseHelper
import joblib
import pandas as pd
import sklearn
from Mqtt.MqttClient import be_notif, mqtt_client

import logging
logging.basicConfig(level=logging.INFO) 


def insert_device_status(payload):
    device_id = payload['device_id']
    status = payload['status']

    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."devices" (device_id, status)
            VALUES (%s, %s)
            ON CONFLICT (device_id)
            DO UPDATE 
                SET status = EXCLUDED.status,
                    last_updated_at = NOW();
        """, (device_id, status))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return False

    finally:
        conn.close()

def insert_device_data(payload):
    device_id = payload['device_id']
    temp = payload['temperature']
    hum = payload['humidity']
    ammonia = payload['ammonia']
    unix_ts = payload['timestamp']
    iso_str = datetime.fromtimestamp(unix_ts, tz=timezone.utc).isoformat()
    offset = payload['offset']

    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()

        cur.execute(f"""
            INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."devices" (device_id, status)
            VALUES (%s, %s)
            ON CONFLICT (device_id) DO NOTHING;
        """, (device_id, "online"))

        # insert ke tabel device_data
        cur.execute(f"""
            INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."device_data"
            (device_id, temperature, humidity, ammonia, timestamp, zone_offset)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (
            device_id,
            temp,
            hum,
            ammonia,
            iso_str, 
            offset
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        return False

    finally:
        conn.close()


def perform_prediction_and_store(today_date_utc):
    start_today, end_today =  get_today_range_for_wib(today_date_utc)  

    conn = DatabaseHelper.connect()
    try:
        # join tabel cages dan daily_activity untuk tanggal hari ini (UTC)
        cur = conn.cursor()
        cur.execute(f"""
            SELECT 
                c.id AS cage_id, 
                c.cage_name, 
                c.current_population,
                c.device_id,
                c.status,
                c.cage_area,
                da.food, 
                da.drink, 
                da.weight, 
                da.death, 
                da.date
            FROM {os.getenv('DATABASE_NAME')}."broiler_app"."cages" c
            LEFT JOIN {os.getenv('DATABASE_NAME')}."broiler_app"."daily_activity" da
                ON c.id = da.cage_id AND da.date BETWEEN %s AND %s
            WHERE c.status = 'active'
        """, (start_today, end_today))

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]  # otomatis dapat nama kolom

        for row in rows:
            row_dict = dict(zip(columns, row))  # ubah row jadi dict

            # device offline -> failed
            device_status = get_device_status(row_dict['device_id'])
            if device_status != 'online':
                store_failed_prediction(row_dict, 2) 
                continue  

            # no daily activity data -> failed
            if row_dict['food'] is None and row_dict['drink'] is None and row_dict['weight'] is None:
                store_failed_prediction(row_dict, 1) 
                continue  

            # perform prediction untuk setiap row
            temp, hum, ammonia, ts, zone_offset = get_device_data(row_dict['device_id'])

            prediction_result, session = perform_prediction(
                row_dict, temp, hum, ammonia, ts, zone_offset)
            
            store_successful_prediction(row_dict, prediction_result, temp, hum, ammonia, ts, zone_offset, session)

    except Exception as e:
        conn.rollback()
        return False

    finally:
        conn.close()

    return True

def store_successful_prediction(data:dict, prediction_result: str, temp, hum, ammonia, ts, zone_offset, session):
    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()
        broiler_prediction_id = str(uuid.uuid4())
        data_query = f"""insert into {os.getenv('DATABASE_NAME')}."broiler_app"."broiler_predictions"
            (id, cage_id, prediction_status, error) values(%s, %s, %s, %s)"""
        cur.execute(data_query, (
            broiler_prediction_id,
            data['cage_id'],
            "success", 
            None
        ))

        data_query = f"""
            INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."broiler_prediction_detail"
            (id, device_id, device_timestamp, device_zone_offset, broiler_prediction_id, 
            prediction_result, humidity, ammo, temperature, food, drink, weight, 
            current_population, cage_area, session)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(data_query, (
                str(uuid.uuid4()),
                data['device_id'],
                ts,
                zone_offset,
                broiler_prediction_id,
                prediction_result,
                hum,
                ammonia,
                temp,
                data['food'],
                data['drink'],
                data['weight'],
                data['current_population'],
                data['cage_area'],
                session
            ))

        # database notifikasi
        if prediction_result == 'abnormal' or prediction_result == 'cannot predict':
            cur.execute("""
                SELECT firebase_id
                FROM "broiler_app"."cages"
                WHERE id = %s
            """, (data['cage_id'],))

            result = [row[0] for row in cur.fetchall()]  # list semua firebase_id

            for user_firebase_id in result:
                # insert ke log_notification
                cur.execute(f"""
                    insert into {os.getenv('DATABASE_NAME')}."broiler_app"."log_notifications"
                        (id, cage_id, cage_name, firebase_id, broiler_prediction_id, read_status, prediction_result)
                    values(%s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    data['cage_id'],
                    data['cage_name'],
                    user_firebase_id,
                    broiler_prediction_id,
                    False,
                    prediction_result
                ))

                # publish mqtt notification 
                logging.info(f"✅ Publishing MQTT notification to {user_firebase_id}")
                be_notif_topic = be_notif.replace("{user_id}", user_firebase_id) 
                payload = {
                    "cage_name": data['cage_name'],
                    "prediction_result": prediction_result,
                }
                mqtt_client.publish(be_notif_topic, json.dumps(payload), qos=1, retain=False)

        conn.commit()
    except Exception as e:
        conn.rollback()
        return False

    finally:
        conn.close()


def store_failed_prediction(data:dict, error: int):
    ## error mapping 
    # 1 -> no daily activity data
    # 2 -> device offline
    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()
        broiler_prediction_id = str(uuid.uuid4())
        data_query = f"""insert into {os.getenv('DATABASE_NAME')}."broiler_app"."broiler_predictions"
            (id, cage_id, prediction_status,error) values(%s, %s, %s, %s)"""
        cur.execute(data_query, (
            broiler_prediction_id,
            data['cage_id'],
            "failed",
            error,
        ))

        conn.commit()


    except Exception as e:
        conn.rollback()
        return False

    finally:
        conn.close()

def get_device_status(device_id):
    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT status
            FROM {os.getenv('DATABASE_NAME')}."broiler_app"."devices"
            WHERE device_id = %s;
        """, (device_id,))

        row = cur.fetchone()
        if row:
            return row[0]  # langsung return nilainya, bukan nama kolom
        else:
            return None

    except Exception as e:
        logging.error(f"Error fetching device status: {e}")
        return None

    finally:
        conn.close()

def get_device_data(device_id):
    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT temperature, humidity, ammonia, timestamp, zone_offset
            FROM {os.getenv('DATABASE_NAME')}."broiler_app"."device_data"
            WHERE device_id = %s
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (device_id,))

        row = cur.fetchone()
        if row:
            # langsung return nilainya, bukan nama kolom
            temp, hum, ammonia, ts, zone_offset = row
            return temp, hum, ammonia, ts, zone_offset
        else:
            return None

    except Exception as e:
        logging.error(f"Error fetching device data: {e}")
        return None

    finally:
        conn.close()
 

def perform_prediction(data:dict, suhu, kelembaban, amoniak, iso_str, offset: int):
    logging.info("PERFORMING PREDICTION...")

    dt = pd.to_datetime(iso_str, utc=True)  # input UTC
    
    # Pastikan iso_str dibaca sebagai UTC-aware datetime
    dt = pd.to_datetime(iso_str, utc=True)

    # Tambahkan offset (misal +7 jam untuk WIB)
    dt_local = dt + pd.Timedelta(hours=offset)
    hour = dt_local.hour

    session = get_session_type(hour)
    dt_local = dt_local.tz_convert(get_timezone_name(offset))

    data_X = {
        "Suhu": suhu,      
        "Kelembaban": kelembaban,   
        "Amoniak": amoniak,   
        "Pakan": data['food'],       
        "Minum": data['drink'],          
        "Bobot": data['weight'],          
        "Populasi": data['current_population'],      
        "Luas Kandang": data['cage_area'],  
        "Hour": hour,            
        "Session": session
    }

    dataFrame = pd.DataFrame([data_X])

    # Convert to float
    X = dataFrame.astype(float).values

    # Load model
    model_path = DirectoryHelper.get_model_dir('rf_timestamp')
    model = joblib.load(model_path)

    # Perform prediction
    result = model.predict(X)

    return determine_prediction_result(result[0]), session


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
    

def get_timezone_name(offset: int) -> str:
    tz_map = {
        7: "Asia/Jakarta",   # WIB
        8: "Asia/Makassar",  # WITA
        9: "Asia/Jayapura"   # WIT
    }
    return tz_map.get(offset, "Asia/Jakarta") 

