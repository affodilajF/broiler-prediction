
import datetime
import os, sys, uuid, requests

from App.Helpers import DatabaseHelper
from App.Helpers.DateHelper import utc_to_offset_iso, offset_to_utc, local_to_offset_iso, now_with_offset_iso_dt
from App.Helpers.DBExceptionsMapper import map_db_exception, BadRequestError
from datetime import datetime, timezone
sys.path.append(os.getcwd())

import logging
logging.basicConfig(level=logging.INFO)  

    # unix_ts = payload['timestamp']
    # dt_utc = datetime.datetime.utcfromtimestamp(unix_ts) 

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
            DO UPDATE SET status = EXCLUDED.status;
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

    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()

        cur.execute(f"""
            INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."devices" (device_id, status)
            VALUES (%s, %s)
            ON CONFLICT (device_id) DO NOTHING;
        """, (device_id, "online"))

        # # insert ke tabel device_data
        cur.execute(f"""
            INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."device_data"
            (device_id, temperature, humidity, ammonia, timestamp)
            VALUES (%s, %s, %s, %s, %s);
        """, (
            device_id,
            temp,
            hum,
            ammonia,
            unix_ts
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        return False

    finally:
        conn.close()


