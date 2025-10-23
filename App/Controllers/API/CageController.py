import os, sys, uuid, requests

from App.Helpers import DatabaseHelper
from App.Helpers.DateHelper import get_today_range_utc, utc_to_offset_iso, offset_to_utc
from datetime import datetime
sys.path.append(os.getcwd())

import logging
logging.basicConfig(level=logging.INFO)  

import os
import uuid

from App.Helpers.DBExceptionsMapper import map_db_exception, BadRequestError

def add_cage(firebase_id, initial_population, cage_area, device_id, cage_name):
    required_fields = {
        "firebase_id": firebase_id,
        "initial_population": initial_population,
        "cage_area": cage_area,
        "device_id": device_id,
        "cage_name": cage_name
    }

    missing = [key for key, value in required_fields.items() if not value]
    if missing:
        raise BadRequestError(f"Missing required fields: {', '.join(missing)}")
    
    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()

        # insert device_id ke tabel devices (kalau sudah ada, abaikan)
        cur.execute(f"""
            INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."devices" (device_id, status)
            VALUES (%s, %s)
            ON CONFLICT (device_id) DO NOTHING;
        """, (device_id, "offline"))

        cage_id = str(uuid.uuid4())
        status = 'non-active'

        # insert ke tabel cages
        cur.execute(f"""
            INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."cages"
            (id, cage_name, firebase_id, initial_population, current_population, cage_area, status, device_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            cage_id,
            cage_name,
            firebase_id,
            initial_population,
            initial_population,  # current_population awal = initial_population
            cage_area,
            status,
            device_id,
        ))

        conn.commit()

        return {
            "cage_id": cage_id,
            "cage_name": cage_name,
            "initial_population": initial_population,
            "current_population": initial_population,
            "cage_area": cage_area,
            "status": status,
            "device_id": device_id,
        }

    except Exception as e:
        conn.rollback()
        raise map_db_exception(e)

    finally:
        conn.close()



def activate_cage(cage_id, date_activated_str, offset_str="+00:00"):
    try:
        date_activated_utc = offset_to_utc(date_activated_str, offset_str)
    except Exception as e:
        # error parsing date dari FE → Bad Request
        raise BadRequestError(f"Invalid date format: {date_activated_str}")

    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()

        # update cages status
        cur.execute(f"""
            UPDATE {os.getenv('DATABASE_NAME')}."broiler_app"."cages"
            SET status = %s
            WHERE id = %s;
        """, ('active', cage_id))

        # insert ke cage_activation_detail (UTC)
        cur.execute(f"""
            INSERT INTO {os.getenv('DATABASE_NAME')}."broiler_app"."cage_activation_detail"
            (cage_id, date_activated)
            VALUES (%s, %s);
        """, (cage_id, date_activated_utc))

        conn.commit()

        return {
            "cage_id": cage_id,
            "date_activated": date_activated_utc.isoformat(),
            "status": "active"
        }

    except Exception as e:
        conn.rollback()
        raise map_db_exception(e)

    finally:
        conn.close()


def get_cage_data(firebase_id, offset_str="+00:00"):
    data_query = f"""
        SELECT 
            c.id,
            c.initial_population,
            c.current_population,
            c.cage_area,
            c.status,
            cad.date_activated,
            c.device_id,
            d.status AS device_status,
            c.created_at,
            c.cage_name
        FROM {os.getenv('DATABASE_NAME')}."broiler_app"."cages" c
        LEFT JOIN LATERAL (
            SELECT cad.date_activated
            FROM {os.getenv('DATABASE_NAME')}."broiler_app"."cage_activation_detail" cad
            WHERE cad.cage_id = c.id
            ORDER BY cad.created_at DESC
            LIMIT 1
        ) cad ON TRUE
        LEFT JOIN {os.getenv('DATABASE_NAME')}."broiler_app"."devices" d 
            ON d.device_id = c.device_id
        WHERE c.firebase_id = %s
        ORDER BY c.created_at DESC;
    """
    array_data = DatabaseHelper.perform_database_query_v2(data_query, (firebase_id,)) or []

    return [
        {
            "id": row[0],
            "initial_population": row[1],
            "current_population": row[2],
            "cage_area": row[3],
            "status": row[4],
            "date_activated":  utc_to_offset_iso(row[5], offset_str) if row[5] else None,
            "device_id": row[6],
            "device_status": row[7],  # <- status dari tabel devices
            "created_at": utc_to_offset_iso(row[8], offset_str) if row[8] else None,
            "cage_name": row[9],
        }
        for row in array_data
    ]

def get_cage_data_v2(firebase_id, offset_str="+00:00"): 
    data_query = f"""
        SELECT 
            c.id,
            c.initial_population,
            c.current_population,
            c.cage_area,
            c.status,
            cad.date_activated,
            c.device_id,
            c.created_at,
            c.cage_name
        FROM {os.getenv('DATABASE_NAME')}."broiler_app"."cages" c
        LEFT JOIN LATERAL (
            SELECT cad.date_activated
            FROM {os.getenv('DATABASE_NAME')}."broiler_app"."cage_activation_detail" cad
            WHERE cad.cage_id = c.id
            ORDER BY cad.created_at DESC
            LIMIT 1
        ) cad ON TRUE
        LEFT JOIN {os.getenv('DATABASE_NAME')}."broiler_app"."devices" d 
            ON d.device_id = c.device_id
        WHERE c.firebase_id = %s
        ORDER BY c.created_at DESC;
    """
    cages = DatabaseHelper.perform_database_query_v2(data_query, (firebase_id,)) or []
    result = []

    # ambil tanggal hari ini (UTC)
    start_today_utc, end_today_utc =  get_today_range_utc(offset_str)
    logging.info(f"P start date (UTC): {start_today_utc}")
    logging.info(f"P end date (UTC): {end_today_utc}")   

    for cage in cages:
        cage_id = cage[0]

        # Ambil broiler_prediction hari ini untuk cage ini
        prediction_query = f"""
            SELECT id, prediction_status, error, created_at
            FROM {os.getenv('DATABASE_NAME')}."broiler_app"."broiler_predictions"
            WHERE cage_id = %s
            AND created_at BETWEEN %s AND %s
        """
        predictions = DatabaseHelper.perform_database_query_v2(
            prediction_query, (cage_id, start_today_utc, end_today_utc)
        ) or []

        prediction_result = []
        for pred in predictions:
            pred_id = pred[0]
            prediction_status = pred[1]

            # Jika sukses, ambil detailnya
            if prediction_status == "success":
                detail_query = f"""
                    SELECT device_id, humidity, ammo, temperature, prediction_result
                    FROM {os.getenv('DATABASE_NAME')}."broiler_app"."broiler_prediction_detail"
                    WHERE broiler_prediction_id = %s
                    LIMIT 1
                """
                d = DatabaseHelper.perform_database_query_v2(detail_query, (pred_id,))[0]

                prediction_details = {
                    "device_id": d[0],
                    "humidity": d[1],
                    "ammo": d[2],
                    "temperature": d[3],
                    "prediction_result": d[4],
                    # "food": d[4],
                    # "drink": d[5],
                    # "weight": d[6],
                    # "current_population": d[7],
                    # "cage_area": d[8],
                    # "session": d[9],
                    # "created_at": utc_to_offset_iso(d[10], offset_str) if d[10] else None,
                }
            else:
                prediction_details = None  # atau {} / [] sesuai format API kamu

            prediction_result.append({
                "prediction_status": prediction_status,
                "error": pred[2],
                "predicted_at": utc_to_offset_iso(pred[3], offset_str) if pred[3] else None,
                "prediction_details": prediction_details
            })

        result.append({
            "id": cage[0],
            "initial_population": cage[1],
            "current_population": cage[2],
            "cage_area": cage[3],
            "cage_status": cage[4],
            "date_activated": utc_to_offset_iso(cage[5], offset_str) if cage[5] else None,
            "device_id": cage[6],
            # "device_status": cage[7],
            "created_at": utc_to_offset_iso(cage[7], offset_str) if cage[7] else None,
            "cage_name": cage[8],
            "prediction_result_data": prediction_result,
        })

    return result
