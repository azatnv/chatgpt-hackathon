import psycopg2
import os
from dotenv import load_dotenv, find_dotenv

from datetime import date

from utils import get_current_sunday, get_next_monday, get_next_sunday

load_dotenv(find_dotenv())
DATABASE_NAME= os.environ.get('DATABASE_NAME')
DATABASE_USER= os.environ.get('DATABASE_USER')
DATABASE_PASSWORD= os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST= os.environ.get('DATABASE_HOST')
DATABASE_PORT= os.environ.get('DATABASE_PORT')


def get_tree_nearest_events():
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


def get_week_events(from_date, to_date):
    conn = psycopg2.connect(
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT
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
            WHERE post.event_date >= '{str(from_date)}' and post.event_date <= '{str(to_date)}'
            ORDER BY post.event_date
            """)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_current_week_events():
    current_day = date.today()
    current_sunday = get_current_sunday()
    return get_week_events(current_day, current_sunday)


def get_next_week_events():
    next_day = get_next_monday()
    next_sunday = get_next_sunday()
    return get_week_events(next_day, next_sunday)


def set_suggested_event_source(user_id, username, url):
    conn = psycopg2.connect(
        database=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT
    )
    cur = conn.cursor()
    cur.execute(f"INSERT INTO suggested_event_sources (user_id, username, url) VALUES ({user_id}, '{username}', '{url}')")
    conn.commit()
    conn.close()
