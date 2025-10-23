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


def get_notification_history(firebase_id, offset_str):
    # Ambil notifikasi user
    query = f"""
        SELECT 
            id,
            cage_id,
            cage_name,
            broiler_prediction_id,
            read_status,
            prediction_result,
            created_at
        FROM {os.getenv('DATABASE_NAME')}."broiler_app"."log_notifications"
        WHERE firebase_id = %s
        ORDER BY created_at DESC;
    """

    array_data = DatabaseHelper.perform_database_query_v2(query, (firebase_id,)) or []

    result = []

    for row in array_data:
        broiler_prediction_id = row[3]

        # Ambil detail prediksi untuk notifikasi ini
        query2 = f"""
            SELECT 
                device_id,
                humidity,
                ammo,
                temperature
            FROM {os.getenv('DATABASE_NAME')}."broiler_app"."broiler_prediction_detail"
            WHERE broiler_prediction_id = %s
            ORDER BY created_at DESC;
        """
        array_data2 = DatabaseHelper.perform_database_query_v2(query2, (broiler_prediction_id,)) or []

        # Masukkan detail prediksi ke notifikasi
        prediction_details = [
            {
                "device_id": drow[0],
                "humidity": drow[1],
                "ammo": drow[2],
                "temperature": drow[3],
                "prediction_result": row[5],
            }
            for drow in array_data2
        ]

        # Format notifikasi
        result.append({
            "id": row[0],
            "cage_id": row[1],
            "cage_name": row[2],
            "broiler_prediction_id": broiler_prediction_id,
            "read_status": row[4],
            "created_at": utc_to_offset_iso(row[6], offset_str) if row[6] else None,
            "prediction_details": prediction_details
        })

    return result


def update_notification_status(notification_ids):
    """
    Update read_status untuk banyak notifikasi sekaligus.

    Args:
        notification_ids (list[str]): list id notifikasi
        read_status (bool/int/str): status baru
    """
    if not notification_ids:
        raise BadRequestError("No notification IDs provided.")

    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()

        query = f"""
            UPDATE {os.getenv('DATABASE_NAME')}."broiler_app"."log_notifications"
            SET read_status = %s
            WHERE id = ANY(%s);
        """
        cur.execute(query, (True, notification_ids))
        conn.commit()

        return {"message": f"{len(notification_ids)} notifications updated successfully."}

    except Exception as e:
        conn.rollback()
        raise map_db_exception(e)

    finally:
        conn.close()

