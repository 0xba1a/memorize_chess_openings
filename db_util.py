import json
import mysql.connector
import os
import json

server=os.environ['DB_SERVER']
uname=os.environ['DB_USER']
pwd=os.environ['DB_PASS']

g_conn = None
g_cursor = None

def get_cursor():
    global g_conn, g_cursor
    if g_conn:
        return g_cursor
    g_conn = mysql.connector.connect(host=server, user=uname, password=pwd, database="chess")
    if g_conn is None:
        print("Could not connect to db")
        return None
    g_cursor = g_conn.cursor()
    return g_cursor


def db_commit(cursor):
    g_cursor.commit()
    

def commit_and_close(cursor):
    global g_conn, g_cursor
    g_conn.commit()
    g_conn.close()
    g_conn = None
    g_cursor = None

def get_new_question_id():
    #conn = mysql.connector.connect(host=server, user=uname, password=pwd, database="chess")
    cursor = get_cursor()
    cursor.execute("SELECT MAX(id) FROM questions")
    result = cursor.fetchone()
    max_id = result[0]
    if result[0] is None:
        max_id = 0
    return max_id + 1