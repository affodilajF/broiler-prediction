import os
import psycopg2
from dotenv import load_dotenv

# Load environment
load_dotenv(".env.dev", override=True)

# Ambil info database dari environment
username = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_USER_PASSWORD', '')  # kosong kalau --insecure
db_name = os.getenv('DATABASE_NAME')
db_port = os.getenv('DATABASE_PORT')
db_host = os.getenv('DATABASE_HOST')

# URL koneksi CockroachDB (sslmode=disable)
db_url = f'postgresql://{username}:{password}@{db_host}:{db_port}/{db_name}?sslmode=disable'

# Path ke file SQL migration (fix path)
sql_file_path = "/broiler-model-api/Database/Migrations/database-migration-20240822.sql"

# Baca isi file SQL
with open(sql_file_path, "r") as f:
    sql_commands = f.read()

# Jalankan SQL
try:
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_commands)
        conn.commit()
        print("Migration berhasil dijalankan!")

except Exception as e:
    print("Migration gagal:", e)
