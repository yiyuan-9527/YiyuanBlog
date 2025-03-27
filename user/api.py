from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from user.models import User
from user.schemas import CreateUserRequest, LoginRequest, RefreshTokenRequest
from YiyuanBlog.auth import (
    JWTAuth,
    generate_access_token,
    generate_refresh_token,
    refreshed_token,
)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
router = Router()


@router.get(
    path='/users/',
    response=list[str],
    summary='取得使用者列表',
    auth=JWTAuth(),
)
def get_users(request: HttpRequest) -> list[str]:
    """
    取得所有使用者, 測驗 JWT token
    """
    # 確保一定會回傳一個列表
    users = User.objects.all()

    return [user.email for user in users]


@router.post(
    path='/users/create/',
    response={201: dict},
    summary='新增使用者(註冊)',
)
def create_user(request: HttpRequest, payload: CreateUserRequest) -> tuple[int, dict]:
    """
    新增使用者(註冊)
    """
    # 檢查 email 是否已存在
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(409, '使用者 email 已存在')

    user = User.objects.create(
        email=payload.email,
    )
    # 使用 set_password() 設定密碼，這樣密碼會被加密
    user.set_password(raw_password=payload.password)
    user.save()

    return 201, {'id': user.id, 'email': user.email}


@router.post(
    path='/users/login/',
    response={200: dict},
    summary='使用者登入',
)
def login_user(request: HttpRequest, payload: LoginRequest) -> dict[str, str]:
    """
    登入使用者
    """
    # django 內建的 authenticate() 方法
    user = authenticate(request, email=payload.email, password=payload.password)

    # 檢查資料庫有沒有輸入的帳號密碼
    if user is None:
        return HttpError(401, '帳號或密碼錯誤')

    # 帶 token 回傳
    access_token = generate_access_token(user.id, user.email)
    refresh_token = generate_refresh_token(user.id, user.email)
    print('登入成功')
    return {
        'status': 'success',
        'access_token': access_token,
        'refresh_token': refresh_token,
    }


@router.post(
    path='/users/logout/',
    response={200: dict},
    summary='使用者登出',
    auth=JWTAuth(),
)
def logut_user(request: HttpRequest) -> dict[str, str]:
    """
    登出使用者
    """
    # 前端負責刪除 access token 和 refresh token
    return {
        'status': 'success',
        'message': '登出成功',
    }


@router.post(
    path='/users/refresh/',
    response={200: dict},
    summary='刷新 token',
)
def refresh(request: HttpRequest, payload: RefreshTokenRequest) -> dict[str, str]:
    """
    刷新 token
    """
    new_access_token = refreshed_token(payload.refresh_token)
    print('刷新成功')
    return {
        'status': 'success',
        'access_token': new_access_token,
    }
