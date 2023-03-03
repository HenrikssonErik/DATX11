from typing import Literal
from flask import jsonify, request, Request, Response  # , jsonify
from ..Database.connector import get_conn_string
import psycopg2


def user_registration(data: Request.form) -> tuple[str, Literal[200, 406]]:
    salt = 100
    
    encodedPass = data['password'] + str(salt)
    
    

    conn = psycopg2.connect(get_conn_string())
    with conn:
        with conn.cursor() as cur:
            try: 
                query = """INSERT INTO UserData
                (cid, email, passphrase, salt) 
                VALUES (%s, %s, %s, %s);"""
                cur.execute(query, (
                    data['cid'], 
                    data['email'], 
                    encodedPass, 
                    salt
                    ))
                status = 'OK'
                res_code = 200
            except:
                status = 'already_registered'
                res_code = 406
                
    conn.close()
    return status, res_code
    

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
