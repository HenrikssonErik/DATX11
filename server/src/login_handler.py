from datetime import datetime, timedelta
import json
from typing import Literal
from flask import jsonify, request, Request, Response
import bcrypt
# from werkzeug.security import gen_salt, generate_password_hash, check_password_hash
from .connector import get_conn_string
import psycopg2
import string
import jwt
import random

__SECRET_KEY: str = None


def createKey():
    global __SECRET_KEY
    __SECRET_KEY = random_string()


def random_string() -> str:
    # length of key, with 8 chars it takes aproxiamtley 1 year to brute force, we use 40 chars
    length = 40
    letters_and_digits = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))


def check_data_input(cid: str, email: str, pwd: str) -> tuple[str, Literal[200, 400]]:
    if not cid.isalpha():
        return 'unallowed_tokens', 400
    if not email:
        return 'email_missing', 400
    if not email == cid + "@chalmers.se":
        return "wrong_format", 400
    allowed_characters = set(string.ascii_letters + string.digits +
                             string.punctuation)
    if not set(pwd) <= allowed_characters:
        return "pass_not_ok", 400
    return "OK", 200


# Break this god-function up if possible.
def user_registration(data: Request.form) -> tuple[str, Literal[200, 400, 406]]:

    email: str = data['email']
    cid: str = data['cid']
    pwd = data['password']

    invalid_data = check_data_input(cid, email, pwd)

    if (invalid_data[1] != 200):
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
            except Exception as e:
                print(e)
                status = 'already_registered'
                res_code = 406

    conn.close()
    return status, res_code


def log_in(email: str, password: str) -> tuple[str, Literal[200, 401]]:
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT userId, passphrase FROM UserData
                            WHERE userdata.email = %s"""
                cur.execute(query_data, (email,))
                data = cur.fetchone()
                id = data[0]
                passphrase: bytes = data[1].tobytes()
        conn.close()
        if not data:
            raise Exception("Wrong Credentials")
    # use the line below to check for correct password, (password is from frontend, passphrase and salt i db)
        if (bcrypt.checkpw(password.encode('utf8'), passphrase)):
            token = create_token(id)
            return token, 200
        else:
            raise Exception("Wrong Credentials")

    except Exception as e:
        print(e)
        return "Wrong Credentials", 401


def create_token(id: int) -> dict:
    data = {'iss': 'Hydrant',
            'id': id,
            'exp': datetime.utcnow() + timedelta(hours=1)
            }
    # generate secret key, set exp-time

    token = jwt.encode(payload=data, key=__SECRET_KEY)
    return {'Token': token}


def verify_token(token: str) -> int:
    try:
        # Verify and decode the token
        decoded_token: dict = jwt.decode(token, __SECRET_KEY,
                                         algorithms=['HS256'])
        # If decoding was successful, return the user id
        return decoded_token['id']

    except jwt.ExpiredSignatureError:
        # If the token has expired, raise an exception
        raise Exception('Invalid token')

    except jwt.InvalidTokenError:
        # If the token is invalid, raise an exception
        raise Exception('Invalid token')

# TODO method to construct secret key
