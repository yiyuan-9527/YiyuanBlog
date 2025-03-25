from django.contrib.auth import authenticate
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from user.models import User
from user.schemas import CreateUserRequest, LoginRequest
from YiyuanBlog.auth import JWTAuth, create_access_token

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

    # 如果沒有使用者，回傳空列表，而不是 None
    if not users:
        return []

    return [user.username for user in users]


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
    user = authenticate(request, email=payload.email, password=payload.password)
    # 檢查資料庫有沒有輸入的帳號密碼
    if user is None:
        return HttpError(401, '帳號或密碼錯誤')

    # 帶 token 狀態
    token = create_access_token(user.id, user.email)
    return {'status': 'success', 'token': token}
