from flask import request, Request  # , jsonify
from ..Database.connector import get_conn_string
import psycopg2


def user_registration(data: Request):

    conn = psycopg2.connect(get_conn_string())
    print("hej")
    with conn:
        with conn.cursor() as cur:
            print("Connection to db")
    conn.close()
