from datetime import datetime, timedelta, timezone
from typing import Optional

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
ACCESS_TOKEN_EXPIRATION = 8  # 8 周
REFSHE_TOKEN_EXPIRATION = 16  # 16 周


class JWTAuth(HttpBearer):
    """
    嚴格的 JWT 認證類別
    - 嚴格認證, 使用者必須要登入
    """

    def authenticate(self, request: HttpRequest, token: str) -> AbstractUser:
        try:
            # 解碼 token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # 確認是訪問 token
            if payload.get('type') != 'access':
                raise HttpError(401, '無效的 access token')

            # 從 payload 取得信箱
            email = payload.get('email')
            if email is None:
                raise HttpError(401, '無效的 token: 缺少信箱')

            # 透過 email 確認 user 是否存在
            user = User.objects.filter(email=email).first()
            if user is None:
                raise HttpError(401, '找不到使用者')
            print(f'使用嚴格認證, 目前使用者: {user}')
            return user  # 回傳 user 物件, 方便在 API 使用

        except jwt.ExpiredSignatureError:
            raise HttpError(401, '逾期 Token')
        except jwt.InvalidTokenError as e:
            print(f'失效 token: {e}')
            raise HttpError(401, f'失效 token: {str(e)}')


# 手動寫的可選認證
def get_optional_user(request: HttpRequest) -> Optional[AbstractUser]:
    """
    輔助函式
    """
    auth_value = request.headers.get('Authorization')
    if not auth_value:
        print('訪客使用者, 無須認證')
        return None

    token = auth_value.split(' ')[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') == 'access':
            email = payload.get('email')
            if email:
                user = User.objects.filter(email=email).first()
                print(f'使用可選認證, 目前使用者: {user}')
                return user

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        print('解碼錯誤, 認定為訪客')
        return None


# 產生 access token
def generate_access_token(user_id: int, email: str) -> str:
    """
    生成訪問 token
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'type': 'access',
        'iat': datetime.now(timezone.utc),  # 生成時間
        'exp': datetime.now(timezone.utc)
        + timedelta(weeks=ACCESS_TOKEN_EXPIRATION),  # 到期時間
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# 產生 refresh token
def generate_refresh_token(user_id: int, email: str) -> str:
    """
    生成刷新 token
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'type': 'refresh',
        'iat': datetime.now(timezone.utc),  # 生成時間
        'exp': datetime.now(timezone.utc)
        + timedelta(weeks=REFSHE_TOKEN_EXPIRATION),  # 到期時間
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# 刷新 token
def refreshed_token(refresh_token: str) -> str:
    try:
        # 解碼刷新 token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # 確認是刷新 token
        if payload.get('type') != 'refresh':
            raise HttpError(401, '無效的 refresh token')

        # 透過 email 取得 user
        email = payload.get('email')
        user = User.objects.filter(email=email).first()

        # 確認使用者存在
        if user is None:
            raise HttpError(401, '找不到使用者')

        # 生成新的 access token
        new_access_token = generate_access_token(user.id, user.email)

        return new_access_token

    except jwt.ExpiredSignatureError:
        raise HttpError(401, 'refresh token 已過期, 請重新登入')
    except jwt.InvalidTokenError:
        raise HttpError(401, '無效的 refresh token')
