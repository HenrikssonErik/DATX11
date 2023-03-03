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


def log_in(email: str, password: str) -> str:
    conn = psycopg2.connect(dsn=get_conn_string())
    with conn:
        with conn.cursor() as cur:
            query_data = """SELECT userId, passphrase, salt FROM UserData
                        WHERE userdata.email = %s"""
            print(type(email))
            print(email)
            cur.execute(query_data, (email,))
            data = cur.fetchone()
            print(data)
            id = data[0]
            password = data[1]
            salt = data[2]
    conn.close()
    #TODO: check h^2 + salt = password
    #create token
    #return appropriate message

    return "token"
