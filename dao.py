import datetime

import psycopg2
import os
from dotenv import load_dotenv, find_dotenv
from datetime import date

from utils import topics2tag_id

load_dotenv(find_dotenv())
DATABASE_NAME = os.environ.get('DATABASE_NAME')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_PORT = os.environ.get('DATABASE_PORT')


def get_db_connection():
    return psycopg2.connect(
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT
        )


def get_communities():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT comm_name, comm_id, comm_img, comm_istelegram FROM community")
    rows = cur.fetchall()
    conn.close()

    return rows


all_groups = get_communities()


def get_events_from_date_interval(from_date, to_date):
    conn = get_db_connection()
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


def get_actual_events():
    conn = get_db_connection()
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
            WHERE post.event_date >= '{str(datetime.datetime.now())}' 
            OR post.event_date = '{str(datetime.datetime(date.today().year, date.today().month, date.today().day))}'
            ORDER BY post.event_date
            """)
    rows = cur.fetchall()
    conn.close()

    return rows


def get_actual_events_by_topic(topic_name: str):
    conn = get_db_connection()
    tag_id = topics2tag_id[topic_name]
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
                FROM tags
                JOIN post ON tags.comm_id = post.comm_id AND tags.post_id = post.post_id
                JOIN community ON post.comm_id = community.comm_id
                WHERE (post.event_date >= '{str(datetime.datetime.now())}' 
                OR post.event_date = '{str(datetime.datetime(date.today().year, date.today().month, date.today().day))}')
                AND tags.tag_id = {tag_id}
                ORDER BY post.event_date
                """)
    rows = cur.fetchall()
    conn.close()

    return rows


def get_week_events():
    conn = get_db_connection()
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
            WHERE (post.event_date >= '{str(datetime.datetime.now())}' 
            OR post.event_date = '{str(datetime.datetime(date.today().year, date.today().month, date.today().day))}')
            AND post.event_date <= '{str(date.today() + datetime.timedelta(7))}'
            ORDER BY post.event_date
            """)
    rows = cur.fetchall()
    conn.close()

    return rows


def set_suggested_event_source(user_id, username, url):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO suggested_event_sources (user_id, username, url) "
                f"VALUES ({user_id}, '{username}', '{url}')")
    conn.commit()
    conn.close()


def set_suggested_functionality(user_id, username, suggestion):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO suggested_functionality (user_id, username, suggestion) "
                f"VALUES ({user_id}, '{username}', '{suggestion}')")
    conn.commit()
    conn.close()


def check_new_user(user_id, username):
    is_new = False
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
    rows = cur.fetchall()
    if len(rows) == 0:
        cur.execute(f"INSERT INTO users (user_id, username, event_clicks, community_clicks, calendar_clicks) "
                    f"VALUES ({user_id}, '{username}', 0, 0, 0)")
        is_new = True
        conn.commit()
    conn.close()

    return is_new


def get_users_count():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) user_id FROM users")
    rows = cur.fetchall()
    count = rows[0][0]
    conn.close()

    return count


def get_user_id_list():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()
    conn.close()

    return rows


def set_user_start_date(user_id, username):
    if check_new_user(user_id, username):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"UPDATE users SET user_start_date = TIMESTAMP '{datetime.datetime.now()}' WHERE user_id = {user_id}")
        cur.execute(f"UPDATE users SET user_last_date = TIMESTAMP '{datetime.datetime.now()}' WHERE user_id = {user_id}")
        conn.commit()
        conn.close()


def set_user_last_date(user_id, username, counter=""):
    check_new_user(user_id, username)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET user_last_date = TIMESTAMP '{datetime.datetime.now()}' WHERE user_id = {user_id}")
    cur.execute(f"UPDATE users SET username = '{username}' WHERE user_id = {user_id}")
    if counter == "event":
            cur.execute(f"SELECT event_clicks FROM users WHERE user_id = {user_id}")
            rows = cur.fetchall()
            count = rows[0][0]
            cur.execute(f"UPDATE users SET event_clicks = '{count + 1}' WHERE user_id = {user_id}")
    elif counter == "community":
            cur.execute(f"SELECT community_clicks FROM users WHERE user_id = {user_id}")
            rows = cur.fetchall()
            count = rows[0][0]
            cur.execute(f"UPDATE users SET community_clicks = '{count + 1}' WHERE user_id = {user_id}")
    elif counter == "calendar":
            cur.execute(f"SELECT calendar_clicks FROM users WHERE user_id = {user_id}")
            rows = cur.fetchall()
            count = rows[0][0]
            cur.execute(f"UPDATE users SET calendar_clicks = '{count + 1}' WHERE user_id = {user_id}")
    conn.commit()
    conn.close()


def log_action(action, user_id, username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO users_log (timestamp, action, user_id, username) "
                f"VALUES ('{datetime.datetime.now()}', '{action}', {user_id}, '{username}')")

    conn.commit()
    conn.close()
