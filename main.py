import psycopg2
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
DATABASE_NAME= os.environ.get('DATABASE_NAME')
DATABASE_USER= os.environ.get('DATABASE_USER')
DATABASE_PASSWORD= os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST= os.environ.get('DATABASE_HOST')
DATABASE_PORT= os.environ.get('DATABASE_PORT')

def get_events():
    conn = psycopg2.connect(
        database = DATABASE_NAME,
        user = DATABASE_USER,
        password = DATABASE_PASSWORD,
        host = DATABASE_HOST,
        port = DATABASE_PORT
    )
    cur = conn.cursor()
    cur.execute("SELECT post_url,post_date FROM post order by post_date desc limit 3;")
    rows = cur.fetchall()
    conn.close()
    return rows

#группы
def get_communities():
    conn = psycopg2.connect(
        database = DATABASE_NAME,
        user = DATABASE_USER,
        password = DATABASE_PASSWORD,
        host = DATABASE_HOST,
        port = DATABASE_PORT
    )
    cur = conn.cursor()
    cur.execute("SELECT comm_name FROM community;")
    rows = cur.fetchall()
    conn.close()
    return rows


print(get_communities())
