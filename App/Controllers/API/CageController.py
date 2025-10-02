import os, sys, uuid, requests

from App.Helpers import DatabaseHelper
from App.Helpers.DateHelper import utc_to_offset_iso, offset_to_utc
from datetime import datetime
sys.path.append(os.getcwd())

import logging
logging.basicConfig(level=logging.INFO)  

import os
import uuid

from App.Helpers.DBExceptionsMapper import map_db_exception, BadRequestError
import psycopg2


def add_cage(firebase_id, initial_population, cage_area, device_id, cage_name):
    logging.info("cekcek2")
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
            "created_at": utc_to_offset_iso(row[7], offset_str) if row[7] else None,
            "cage_name": row[8],
        }
        for row in array_data
    ]


