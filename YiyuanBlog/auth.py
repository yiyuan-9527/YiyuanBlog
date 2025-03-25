from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings

# from typing import Any, Optional
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
from ninja.errors import HttpError
from ninja.security import HttpBearer

from user.models import User

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
TOKEN_EXPIRATION = 240  # 240 單位


class JWTAuth(HttpBearer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def authenticate(self, request: HttpRequest, token: str) -> AbstractUser:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(str(payload))
            email = payload.get('email')

            # 從 payload 取得信箱
            if email is None:
                raise HttpError(401, 'Invalid token: Missing user_id')

            # 確認 user 是否存在
            user = User.objects.filter(email=email).first()
            if user is None:
                raise HttpError(401, '找不到使用者')
            print(str(user))
            print('驗證成功')
            return user  # 回傳 user 物件, 方便在 API 使用
        except jwt.ExpiredSignatureError:
            raise HttpError(401, '逾期 Token')
        except jwt.InvalidTokenError:
            raise HttpError(401, '失效 Token')


# 生成 JWT token 的函數
def create_access_token(user_id: int, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.now(timezone.utc)
        + timedelta(minutes=TOKEN_EXPIRATION),  # 到期日
        'iat': datetime.now(timezone.utc),  # 發行時間
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print('發行成功: ' + token)
    return token


# def create_jwt(user: User) -> str:
#     """
#     產生 JWT
#     """
#     payload = {
#         'user_id': user.id,
#         'email': user.email,
#         'iat': datetime.datetime.now(datetime.timezone.utc),  # 發行時間
#         'exp': datetime.timedelta(minutes=TOKEN_EXPIRATION),  # 到期日
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     print('JWT: ' + token)
#     return token


# def decode_jwt(token: str) -> dict:
#     """
#     解碼與驗證 JWT
#     """
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HttpError(401, 'Token 過期')
#     except jwt.InvalidTokenError:
#         raise HttpError(401, '無效的 Token')
