import psycopg2
import os
from dotenv import load_dotenv, find_dotenv
# from sqlalchemy import

import time
from datetime import date

load_dotenv(find_dotenv())
DATABASE_NAME= os.environ.get('DATABASE_NAME')
DATABASE_USER= os.environ.get('DATABASE_USER')
DATABASE_PASSWORD= os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST= os.environ.get('DATABASE_HOST')
DATABASE_PORT= os.environ.get('DATABASE_PORT')

def get_events():
    current_day = date.today()
    conn = psycopg2.connect(
        database = DATABASE_NAME,
        user = DATABASE_USER,
        password = DATABASE_PASSWORD,
        host = DATABASE_HOST,
        port = DATABASE_PORT
    )
    cur = conn.cursor()
    cur.execute(f"""
    SELECT 
        post.post_url, 
        post.event_title,
        post.event_date,
        post.event_place,
        post.event_short_desc,
        post.event_picture_url,
        community.comm_name
    FROM post
    JOIN community ON post.comm_id = community.comm_id
    WHERE post.event_date >= '{str(current_day)}'
    ORDER BY post.event_date
    LIMIT 3;
    """)
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
    cur.execute("SELECT comm_name, comm_id, comm_img FROM community;")
    rows = cur.fetchall()
    conn.close()
    return rows


all_groups = get_communities()
