import datetime

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from ninja.errors import HttpError

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
TOKEN_EXPIRATION = 60


def create_jwt(user: User) -> str:
    """
    產生 JWT
    """
    payload = {
        'user_id': user.id,
        'email': user.email,
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'exp': datetime.timedelta(minutes=TOKEN_EXPIRATION),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print('JWT: ' + token)
    return token


def decode_jwt(token: str) -> dict:
    """
    解碼與驗證 JWT
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HttpError(401, 'Token 過期')
    except jwt.InvalidTokenError:
        raise HttpError(401, '無效的 Token')
