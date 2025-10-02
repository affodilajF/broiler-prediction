import os, sys, uuid, requests

from App.Helpers import DatabaseHelper
from App.Helpers.DateHelper import utc_to_offset_iso, offset_to_utc, local_to_offset_iso, now_with_offset_iso_dt
from App.Helpers.DBExceptionsMapper import map_db_exception, BadRequestError
from datetime import datetime, timezone
sys.path.append(os.getcwd())

import logging
logging.basicConfig(level=logging.INFO)  

def get_daily_activities(cage_id, offset_str):
    query = f"""
    SELECT id, cage_id, date, food, drink, weight, death, created_at
    FROM {os.getenv('DATABASE_NAME')}."broiler_app"."daily_activity"
    WHERE cage_id = %s;
    """
    rows = DatabaseHelper.perform_database_query_v2(query, (cage_id,)) or []
    return [
        {
            "id": row[0],
            "cage_id": row[1],
            "date": utc_to_offset_iso(row[2], offset_str) if row[2] else None,
            "food": row[3],
            "drink": row[4],
            "weight": row[5],
            "death" : row[6],
            "created_at": utc_to_offset_iso(row[7], offset_str) if row[7] else None,
        }
        for row in rows
    ]


    
def add_daily_activity(cage_id, dailyactivity_date, food, drink, weight, death, offset_str):
    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()
        date_utc = offset_to_utc(dailyactivity_date, offset_str)

        # Ambil tanggal aktivasi cage
        cur.execute(f"""
            SELECT date_activated 
            FROM {os.getenv('DATABASE_NAME')}."broiler_app"."cage_activation_detail"
            WHERE cage_id = %s
        """, (cage_id,))

        result = cur.fetchone()

        if not result:
            raise BadRequestError("Cage has not been created or activated yet.")
    

        date_activated = result[0]

        local_dt = local_to_offset_iso(dailyactivity_date, offset_str)  # return datetime aware
        now_dt = now_with_offset_iso_dt(offset_str)  # return datetime aware

        # validasi apakah date_utc > today
        if local_dt > now_dt:
            raise BadRequestError(
                f"Date {dailyactivity_date} cannot be in the future"
            )
        # Validasi apakah date_utc >= date_activated
        if date_utc < date_activated:
            raise BadRequestError(
                f"Date {date_utc.date()} is before cage activation date {date_activated.date()}"
            )

        # Cek apakah date_utc sudah ada di daily_activity
        cur.execute(f"""
            SELECT EXISTS (
                SELECT 1 FROM {os.getenv('DATABASE_NAME')}."broiler_app"."daily_activity"
                WHERE cage_id = %s AND date = %s
            )
        """, (cage_id, date_utc))

        exists = cur.fetchone()[0]
        
        if exists:
            raise BadRequestError(
                f"Data for date {dailyactivity_date} already exists in daily_activity"
            )

        # ambil current_population
        cur.execute(f"""
            select current_population from {os.getenv('DATABASE_NAME')}."broiler_app"."cages"
            where id = %s
        """, (cage_id,))
        result = cur.fetchone()

        current_population = result[0]
        new_current_population = current_population - death

        # update cages
        cur.execute(f"""
            update {os.getenv('DATABASE_NAME')}."broiler_app"."cages"
            set current_population = %s
            where id = %s
        """, (new_current_population, cage_id))

        # insert daily_activity
        cur.execute(f"""
            insert into {os.getenv('DATABASE_NAME')}."broiler_app"."daily_activity"
            (id, cage_id, date, food, drink, weight, death)
            values (%s, %s, %s, %s, %s, %s, %s)
        """, (str(uuid.uuid4()), cage_id, date_utc, food, drink, weight, death))

        # commit transaksi
        conn.commit()
        return {
            "cage_id": cage_id,
            "date": dailyactivity_date, 
            "food": food,
            "weight": weight, 
            "death": death
        }
    except Exception as e:
        conn.rollback()
        raise map_db_exception(e)
    finally:
        conn.close()
