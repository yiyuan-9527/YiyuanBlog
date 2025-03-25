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
ACCESS_TOKEN_EXPIRATION = 60  # 60 單位
REFSHE_TOKEN_EXPIRATION = 7  # 7 天


class JWTAuth(HttpBearer):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def authenticate(self, request: HttpRequest, token: str) -> AbstractUser:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f'Payload: {payload}')
            email = payload.get('email')

            # 從 payload 取得信箱
            if email is None:
                raise HttpError(401, 'Invalid token: Missing user_id')

            # 透過 email 確認 user 是否存在
            user = User.objects.filter(email=email).first()
            if user is None:
                raise HttpError(401, '找不到使用者')
            print(user)
            return user  # 回傳 user 物件, 方便在 API 使用
        except jwt.ExpiredSignatureError:
            raise HttpError(401, '逾期 Token')
        except jwt.InvalidTokenError as e:
            print(f'失效 token: {e}')
            raise HttpError(401, '失效 token')


# 產生 access token
def generate_access_token(user_id: int, email: str) -> str:
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc)
        + timedelta(seconds=ACCESS_TOKEN_EXPIRATION),  # 到期日
        'iat': datetime.now(timezone.utc),  # 發行時間
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print('發行成功: ' + token)
    return token


# 產生 refresh token

