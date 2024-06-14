import jwt
import datetime
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

def generate_token(data, expiration_days=14):
    expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=expiration_days)
    token = jwt.encode({'data': data, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded['data']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
