from datetime import datetime, timedelta
from typing import Literal
from flask import Request
import bcrypt
from .connector import get_conn_string
import psycopg2
import string
import jwt
import random

__SECRET_KEY: str = None


def createKey():
    """ Creates a secret key, should be called from APP.py at start
      or login/registration will fail"""
    global __SECRET_KEY
    __SECRET_KEY = random_string()


def random_string() -> str:
    """Creates a random string of size 'length' to be used as a secret key
    for encryption and singatures

    For lenght reference: A string of 8 Chars takes aproximatly 1 year to
    brute force with bcryp-signatures."""
    length = 40
    letters_and_digits = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))


def check_data_input(cid: str, email: str,
                     pwd: str) -> tuple[str, Literal[200, 400]]:
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


def user_registration(data: Request.form) -> \
        tuple[dict[str, str], Literal[200, 400, 401, 406]]:

    email: str = data['email']
    cid: str = data['cid']
    pwd: str = data['password']

    invalid_data = check_data_input(cid, email, pwd)

    if (invalid_data[1] != 200):
        return {'error': invalid_data[0]}, invalid_data[1]

    salt: bytes = bcrypt.gensalt()
    hashed_pass: bytes = bcrypt.hashpw(pwd.encode('utf-8'), salt)

    res_query: tuple[dict[str, str], Literal[200, 406]
                     ] = registration_query(cid, email, hashed_pass)

    res_object = (log_in(email, pwd)) if (res_query[1] == 200) else (res_query)

    print(res_object)

    return res_object


def registration_query(cid: str, email: str, hashed_pass: bytes) -> \
        tuple[dict[str, str], Literal[200, 406]]:
    conn = psycopg2.connect(get_conn_string())
    with conn:
        with conn.cursor() as cur:
            try:
                query = """INSERT INTO UserData
                (cid, email, passphrase)
                VALUES (%s, %s, %s);"""
                cur.execute(query, (
                    cid,
                    email,
                    hashed_pass
                ))
                status = 'OK'
                res_code = 200
            except Exception as e:
                print("NOT HERE", e)
                status = 'already_registered'
                res_code = 406
    conn.close()
    return {'error': status}, res_code


def log_in(email: str, password: str) -> tuple[dict[str, str],
                                               Literal[200, 401]]:
    """Checks if the user exists in the database, if so it returns a
    token that the user can use to verify itself"""
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
        if (bcrypt.checkpw(password.encode('utf8'), passphrase)):
            token: dict[str, str] = create_token(id)
            return token, 200
        else:
            raise Exception("Wrong Credentials")

    except Exception as e:
        print(e)
        return {'error': "Wrong Credentials"}, 401


def create_token(id: int) -> dict[str, str]:
    """Creates a token to verify a User that is valid for one hour."""
    data = {'iss': 'Hydrant',
            'id': id,
            'exp': datetime.utcnow() + timedelta(hours=1)
            }
    # generate secret key, set exp-time

    token = jwt.encode(payload=data, key=__SECRET_KEY)
    return {'Token': token}


def verify_token(token: str) -> int:
    """Verifys if a token is issued by this system and if it is still valid.
    Returns the User_id or an error message"""
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
