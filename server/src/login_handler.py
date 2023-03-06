from typing import Literal
from flask import jsonify, request, Request, Response
import bcrypt
#from werkzeug.security import gen_salt, generate_password_hash, check_password_hash
from ..Database.connector import get_conn_string
import psycopg2
import string

def check_data_input(cid: str, email: str, pwd: str) -> tuple[str, Literal[200, 400]]:
    if not cid.isalpha():
        return 'unallowed_tokens', 400
    if not cid:
        return 'cid_missing', 400
    if not email:
        return 'email_missing', 400
    if not email == cid + "@chalmers.se":
        return "wrong_format", 400
    allowed_characters = set(string.ascii_letters + string.digits + string.punctuation)
    if not set(pwd) <= allowed_characters:
        return "pass_not_ok", 400
    return "OK", 200
    
#Break this god-function up if possible.
def user_registration(data: Request.form) -> tuple[str, Literal[200, 400, 406]]:
    
    email: str = data['email'] 
    cid: str = data['cid']
    pwd = data['password']
    
    invalid_data = check_data_input(cid, email, pwd)
    
    if(invalid_data[1] != 200):
        return invalid_data
    
    print(email, "\n", cid, "\n", pwd)
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(pwd.encode('utf-8'), salt)

    conn = psycopg2.connect(get_conn_string())
    with conn:
        with conn.cursor() as cur:
            try: 
                query = """INSERT INTO UserData
                (cid, email, passphrase) 
                VALUES (%s, %s, %s);"""
                cur.execute(query, (
                    data['cid'], 
                    data['email'],
                    hashed_pass
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

    salt = bcrypt.gensalt()
    
    with conn:
        with conn.cursor() as cur:
            query_data = """SELECT userId, passphrase FROM UserData
                        WHERE userdata.email = %s"""
            cur.execute(query_data, (email,))
            data = cur.fetchone()
            id = data[0]
            passphrase: bytes = data[1].tobytes()
    conn.close()
    print(password.encode('utf8') + salt)
    print(bcrypt.hashpw(password.encode('utf8') + salt, salt))
    print(bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()))
    print(passphrase)

    #use the line below to check for correct password, (password is from frontend, passphrase and salt i db)
    print(bcrypt.checkpw(password.encode('utf8'), passphrase))
    #test = bcrypt.checkpw(passphrase.encode('utf8') + salt, password)

    #print(test)
    
    #create token
    #return appropriate message

    return "token"
