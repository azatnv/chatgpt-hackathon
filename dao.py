import datetime

import psycopg2
import os
from dotenv import load_dotenv, find_dotenv
from datetime import date

from utils import topics2tag_id, list_to_pg_array_text, list_to_pg_array_int

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
                community.comm_name,
                post.event_duplicates
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
                community.comm_name,
                post.event_duplicates
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
                    community.comm_name,
                    post.event_duplicates
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


def get_actual_events_by_topic_list(topics_list: list):
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
                    community.comm_name,
                    post.event_duplicates
                FROM tags
                JOIN post ON tags.comm_id = post.comm_id AND tags.post_id = post.post_id
                JOIN community ON post.comm_id = community.comm_id
                WHERE (post.event_date >= '{str(datetime.datetime.now())}' 
                OR post.event_date = '{str(datetime.datetime(date.today().year, date.today().month, date.today().day))}')
                AND tags.tag_id = ANY (ARRAY [{list_to_pg_array_int(topics_list)}])
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
        cur.execute(f"INSERT INTO users (user_id, username) "
                    f"VALUES ({user_id}, '{username}')")
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


def get_notifications_user_id_list():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users_notification")
    rows = cur.fetchall()
    conn.close()

    return rows


def log_action(action, user_id, username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO users_log (timestamp, action, user_id, username) "
                f"VALUES ('{datetime.datetime.now()}', '{action}', {user_id}, '{username}')")

    conn.commit()
    conn.close()


def get_user_selected_comm(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT selected_comm FROM users WHERE user_id = {user_id}")
    rows = cur.fetchall()
    conn.close()

    return rows[0][0]


def set_user_selected_comm(user_id, comm):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET selected_comm = ARRAY [{list_to_pg_array_text(comm)}] WHERE user_id = {user_id}")
    conn.commit()
    conn.close()


def check_new_users_notif_row(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT user_id FROM users_notification WHERE user_id = {user_id}")
    rows = cur.fetchall()
    if len(rows) == 0:
        cur.execute(f"INSERT INTO users_notification (user_id)"
                    f"VALUES ({user_id})")
        conn.commit()
    conn.close()


def set_push_interval(user_id, interval):
    check_new_users_notif_row(user_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users_notification SET push_interval = {interval} WHERE user_id = {user_id}")
    conn.commit()
    conn.close()
    set_next_push_date(user_id, datetime.datetime.now() + datetime.timedelta(interval))


def get_push_interval(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT push_interval FROM users_notification WHERE user_id = {user_id}")
    rows = cur.fetchall()
    conn.close()

    return rows[0][0]


def get_user_push_tags(user_id):
    check_new_users_notif_row(user_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT push_tags FROM users_notification WHERE user_id = {user_id}")
    rows = cur.fetchall()
    conn.close()

    return rows[0][0]


def set_user_push_tags(user_id, tags):
    check_new_users_notif_row(user_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users_notification SET push_tags = ARRAY [{list_to_pg_array_int(tags)}] WHERE user_id = {user_id}")
    conn.commit()
    conn.close()


def get_next_push_date(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT next_push_date FROM users_notification WHERE user_id = {user_id}")
    rows = cur.fetchall()
    conn.close()

    return rows[0][0]


def set_next_push_date(user_id, date):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users_notification SET next_push_date = TIMESTAMP '{date}' WHERE user_id = {user_id}")
    conn.commit()
    conn.close()
