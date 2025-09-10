import os, sys, uuid, requests

from App.Helpers import DatabaseHelper
sys.path.append(os.getcwd())

def get_daily_activities(cage_id):
    query = f"""
    SELECT id, cage_id, day, food, drink, weight, current_population, created_at
    FROM {os.getenv('DATABASE_NAME')}."broiler_app"."daily_activity"
    WHERE cage_id = %s;
    """
    rows = DatabaseHelper.perform_database_query_v2(query, (cage_id,)) or []

    columns = ["id","cage_id","day","food","drink","weight","current_population","created_at"]
    return [
        {col: (str(row[i]) if col=="created_at" else row[i]) for i, col in enumerate(columns)}
        for row in rows
    ]


def add_daily_activity(cage_id, food, drink, weight, death, day):
    conn = DatabaseHelper.connect()
    try:
        cur = conn.cursor()

        # ambil current_population
        cur.execute(f"""
            select current_population from {os.getenv('DATABASE_NAME')}."broiler_app"."cages"
            where id = %s
        """, (cage_id,))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Cage ID {cage_id} does not exist.")

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
            (id, cage_id, day, food, drink, weight, current_population)
            values (%s, %s, %s, %s, %s, %s, %s)
        """, (str(uuid.uuid4()), cage_id, day, food, drink, weight, new_current_population))

        # commit transaksi
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
