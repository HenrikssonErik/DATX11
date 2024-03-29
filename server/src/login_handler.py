from datetime import datetime, timedelta
from typing import Literal
from flask import Request
import bcrypt
from .connector import get_conn_string
import psycopg2
import string
import jwt
import random
from .call_ldap import check_against_ldap

__SECRET_KEY: str = None


def create_key():
    """
    Creates a secret key, should be called from APP.py at start
    or login/registration will fail
    """
    global __SECRET_KEY
    with open('./secretkey.cfg') as f:
        __SECRET_KEY = f.readline()


def random_string() -> str:
    """
    Creates a random string of size 'length' to be used as a secret key
    for encryption and singatures

    For length reference: A string of 8 Chars takes aproximatly 1 year to
    brute force with bcryp-signatures."""
    bit_length = 320
    # Generate a list of 286 random bits (0 or 1)
    bitlist = [random.choice([0, 1]) for _ in range(bit_length)]
    # Convert the list of bits to a string
    bitstring = ''.join(str(bit) for bit in bitlist)
    return bitstring


def check_data_input(cid: str, email: str, pwd: str,
                     user_exists: bool) -> tuple[str, Literal[200, 400]]:
    """Validates the inputs from the frontend. If any of these checks are
    not valid, return the appropriate error message and error code as a
    tuple.
    """
    if not cid.isalpha():
        return 'unallowed_tokens', 400
    if not email:
        return 'email_missing', 400
    if not email == cid + "@chalmers.se":
        return "wrong_format", 400
    if not user_exists:
        return "cid_does_not_exist", 400
    if not allowed_password(pwd):
        return "pass_not_ok", 400
    return "OK", 200


def allowed_password(pwd: str) -> bool:
    allowed_characters = set(string.ascii_letters + string.digits +
                             string.punctuation)
    return set(pwd) <= allowed_characters


def create_temp_users(cids: list[str]) -> list[str]:
    cids_do_not_exit_in_chalmers = []
    unallowed_cid = []
    newly_registered = []
    conn = psycopg2.connect(get_conn_string())
    with conn:
        with conn.cursor() as cur:
            query = "INSERT INTO UserData " +\
                    "(chalmersId, userEmail, passphrase, globalRole, fullName) " +\
                    "VALUES (%s, %s, %s, %s, %s ) " +\
                    "on conflict do nothing;"
            for cid in cids:
                if not cid.isalpha():
                    unallowed_cid.append(cid)
                    continue
                maybe_user = check_against_ldap(cid)
                if maybe_user is None:
                    cids_do_not_exit_in_chalmers.append(cid)
                    continue
                else:
                    role, name = maybe_user
                    cur.execute(
                        query,
                        (
                            cid,
                            f"{cid}@chalmers.se",
                            None,
                            role,
                            name
                        )
                    )
                    newly_registered.append(cid)
    conn.close()
    return newly_registered


def new_password(cid, password) -> tuple[dict[str, str], int]:

    if not allowed_password(password):
        return {"status": "pass_not_ok"}, 400
    else:
        salt: bytes = bcrypt.gensalt()
        hashed_pass: bytes = bcrypt.hashpw(password.encode('utf-8'), salt)

        update_status = update_pwd_in_db(cid, hashed_pass)

        return update_status


def update_pwd_in_db(cid: str, pwd: bytes) -> tuple[dict[str, str], int]:
    conn = psycopg2.connect(get_conn_string())

    with conn:
        with conn.cursor() as cur:
            try:

                query = "UPDATE UserData " +\
                        "SET passphrase = %s " +\
                        "WHERE chalmersId = %s;"

                cur.execute(query, (
                    pwd,
                    cid
                ))

                if cur.rowcount == 0:
                    status = 'user_not_found'
                    res_code = 406
                else:
                    status = 'success'
                    res_code = 200
            except Exception:
                status = 'uncaught_error'
                res_code = 500
    conn.close()
    return {'status': status}, res_code


def user_registration(data: Request) -> \
        tuple[dict[str, str], Literal[200, 400, 401, 406, 500]]:
    """
    Registrates the user to the database, then logs in to the user.
    If success, return the token from log_in and success code.
    If the user cannot be created, return error message and error code.

    Creates a bcrypted password to be stored in the database to ensure
    data security, since bcrypted passwords are difficult to brute force.
    """
    email: str = data['email']
    cid: str = data['cid']
    pwd: str = data['password']

    role_name = check_against_ldap(cid)

    # user_exists = False if (role_name[1] is None) else True
    user_exists = role_name is not None

    data_check = check_data_input(cid, email, pwd, user_exists)

    if (data_check[1] != 200):
        return {'status': data_check[0]}, data_check[1]
    if role_name is not None:
        role, name = role_name
        salt: bytes = bcrypt.gensalt()
        hashed_pass: bytes = bcrypt.hashpw(pwd.encode('utf-8'), salt)

        res_query: tuple[
            dict[str, str], Literal[200, 406]
        ] = registration_query(
            cid, email, hashed_pass, role, name
        )
        res_object = ({'token': create_cid_token(cid)}, 200) if (
            res_query[1] == 200) else (res_query)

        return res_object
    else:
        # Unreachable
        return {'status': "Something went wrong"}, 500


def registration_query(cid: str, email: str, hashed_pass: bytes,
                       role: str, name: str) -> \
        tuple[dict[str, str], Literal[200, 406]]:
    """
    Queries the database with the information given.
    If the unique key already is in the database, return error message
    that the user is already registered.

    IntegrityError: https://www.psycopg.org/docs/errors.html Class 23.
    Other exceptions or errors may be added continuously when needed.
    """
    conn = psycopg2.connect(get_conn_string())
    with conn:
        with conn.cursor() as cur:
            try:
                # query = "INSERT INTO UserData " +\
                #     "(cid, email, passphrase, globalRole, fullName) " +\
                #     "VALUES (%s, %s, %s, %s, %s ) "

                query = "INSERT INTO UserData " +\
                    "(chalmersId, userEmail, passphrase, globalRole, fullName) " +\
                    "VALUES (%s, %s, %s, %s, %s ) " +\
                    "ON CONFLICT (chalmersId) DO UPDATE " +\
                    "SET passphrase = EXCLUDED.passphrase " +\
                    "WHERE userdata.chalmersId = EXCLUDED.chalmersId and " +\
                    "userdata.passphrase is null;"

                cur.execute(query, (
                    cid,
                    email,
                    hashed_pass,
                    role,
                    name
                ))

                if cur.rowcount == 0:
                    status = 'already_registered'
                    res_code = 406
                else:
                    status = 'success'
                    res_code = 200
            except psycopg2.IntegrityError:
                status = 'already_registered'
                res_code = 406
    conn.close()
    return {'status': status}, res_code


def user_to_resend_verification_email(cid: str) -> tuple[dict[str, str], int]:
    conn = psycopg2.connect(dsn=get_conn_string())
    with conn:
        with conn.cursor() as cur:
            try:
                query_data = """SELECT userEmail, verifiedAccount
                            FROM UserData
                            WHERE userdata.chalmersId = %s
                                AND userdata.passphrase IS NOT NULL"""
                cur.execute(query_data, (cid,))
                data = cur.fetchone()
                if not data:
                    return {'status': 'no_user'}, 406
                verified = data[1]
                mail = data[0]

                if not verified:
                    response_object = {"email": mail}
                    token = create_cid_token(cid)
                    response_object.update({'token': token})
                    return response_object, 200
                else:
                    return {"status": "already_verified"}, 406
            except Exception:
                return {"status": "unexpected_error"}, 500


def user_to_send_reset_pwd_email(cid: str) -> tuple[dict[str, str], int]:
    conn = psycopg2.connect(dsn=get_conn_string())
    with conn:
        with conn.cursor() as cur:
            try:
                query_data = """SELECT userEmail
                            FROM UserData
                            WHERE userdata.chalmersId = %s
                                AND userdata.passphrase IS NOT NULL"""
                cur.execute(query_data, (cid,))
                data = cur.fetchone()
                if not data:
                    return {'status': 'no_user'}, 406
                mail = data[0]

                response_object = {"email": mail}
                token = create_cid_token(cid)
                response_object.update({'token': token})
                return response_object, 200

            except Exception:
                return {"status": "unexpected_error"}, 500


def log_in(email: str, password: str) -> tuple[dict[str, str],
                                               Literal[200, 401]]:
    """
    Checks if the user exists in the database, if so it returns a
    token that the user can use to verify itself.
    """
    conn = psycopg2.connect(dsn=get_conn_string())

    try:
        with conn:
            with conn.cursor() as cur:
                query_data = """SELECT userId, passphrase, globalrole, verifiedAccount
                            FROM UserData
                            WHERE userdata.userEmail = %s
                            AND userdata.passphrase IS NOT NULL"""
                cur.execute(query_data, (email,))
                data = cur.fetchone()
                id = data[0]
                passphrase: bytes = data[1].tobytes()
                verified = data[3]

        conn.close()
        if not data:
            raise Exception("Wrong Credentials")

        if (bcrypt.checkpw(password.encode('utf8'), passphrase)):
            return_dict: dict[str, str] = {"Token": create_token(id)}
            return_dict['GlobalRole'] = data[2]
            if not verified:
                return {'status': 'not_verified'}, 401
            return return_dict, 200
        else:
            raise Exception("Wrong Credentials")

    except Exception:
        return {'status': "wrong_credentials"}, 401


def create_cid_token(cid: str) -> str:
    """
    Creates a token to verify a User that is valid for 24 hours.
    This token is sent in the verification email to the user registering.
    """
    data = {
        'iss': 'Hydrant',
        'cid': cid,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload=data, key=__SECRET_KEY)
    return token


def verify_and_get_cid(token: str) -> \
        tuple[dict[str, str], Literal[200, 406, 500]]:
    """
    Verifies if a token is issued by this system and if it is still valid.
    Returns the either the cid and success-code, indicator that the cid is
    not present in the database and an errorcode, or raises an error.
    """
    try:
        # Verify and decode the token
        decoded_token: dict = jwt.decode(token, __SECRET_KEY,
                                         algorithms=['HS256'])
        cid: str = decoded_token['cid']

        verification_response: tuple[dict[str, str],
                                     Literal[200, 406, 500]] = \
            verify_user_in_db(cid)
        # If decoding was successful, return the user id

        if (verification_response[1] == 200):
            return {'cid': cid}, 200
        else:
            return verification_response

    except jwt.ExpiredSignatureError as e:
        # If the token has expired, raise an exception

        raise jwt.ExpiredSignatureError('Expired token') from e

    except jwt.InvalidTokenError as e:
        # If the token is invalid, raise an exception

        raise jwt.InvalidTokenError('Invalid token') from e


def verify_user_in_db(cid: str) -> \
        tuple[dict[str, str], Literal[200, 406, 500]]:
    """
    Updates the cid taken to verified=true.
    If the database doesn't contain the cid,
    the function will return that as a status code.
    """
    conn = psycopg2.connect(get_conn_string())
    with conn:
        with conn.cursor() as cur:
            try:
                query = "UPDATE UserData " +\
                    "SET verifiedAccount = TRUE " +\
                    "WHERE chalmersId = %s " +\
                    "AND passphrase IS NOT NULL"
                cur.execute(query, (
                    cid,
                ))

                if (cur.rowcount == 0):
                    conn.close()
                    return {'status': 'no_user_to_verify'}, 406
                status = 'success'
                res_code = 200

            except Exception:
                status = 'uncaught_error'
                res_code = 500

    conn.close()
    return {'status': status}, res_code


def create_token(id: int) -> str:
    """
    Creates a token to verify a User that is valid for one hour.
    """
    data = {'iss': 'Hydrant',
            'id': id,
            'exp': datetime.utcnow() + timedelta(hours=2)
            }

    token = jwt.encode(payload=data, key=__SECRET_KEY)
    return token


def verify_and_get_id(token: str) -> int:
    """
    Verifys if a token is issued by this system and if it is still valid.
    Returns the User_id or an error message
    """

    try:
        # Verify and decode the token
        decoded_token: dict = jwt.decode(token, __SECRET_KEY,
                                         algorithms=['HS256'])
        # If decoding was successful, return the user id
        return decoded_token['id']

    except jwt.ExpiredSignatureError as e:
        # If the token has expired, raise an exception
        e.add_note("Expired token")
        raise e

    except jwt.InvalidTokenError as e:
        # If the token is invalid, raise an exception
        e.add_note("Invalid token")
        raise e
