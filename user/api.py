from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.http import HttpRequest
from ninja import File, Router, UploadedFile
from ninja.errors import HttpError

from shared.images_utils import (
    is_valid_image,
    rename_file,
)
from user.models import User
from user.schemas import (
    CreateUserRequest,
    LoginRequest,
    PrivateUserInfoOut,
    RefreshTokenRequest,
    UpdateUserInfoIn,
    VerifyEmailRequest,
)
from user.utils import EmailVerificationService, create_user_folder
from YiyuanBlog.auth import (
    generate_access_token,
    generate_refresh_token,
    refreshed_token,
)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
router = Router()


@router.get(
    path='/',
    response=list[str],
    summary='取得使用者列表',
)
def get_users(request: HttpRequest) -> list[str]:
    """
    取得所有使用者, 測驗 JWT token
    """
    # 確保一定會回傳一個列表
    users = User.objects.all()

    return [user.email for user in users]


@router.get(
    path='me/',
    response=PrivateUserInfoOut,
    summary='取得使用者資訊',
)
def get_current_user_info(request: HttpRequest) -> PrivateUserInfoOut:
    """
    取得當前使用者資訊
    """
    if not request.auth:
        raise HttpError(401, '請先登入')

    user = request.auth
    return user


@router.post(
    path='register/',
    response={201: dict},
    summary='新增使用者(註冊)',
    auth=None,
)
def register_user(request: HttpRequest, payload: CreateUserRequest) -> tuple[int, dict]:
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

    # 發送驗證信
    EmailVerificationService.send_verification_email(user)
    print('發送驗證信成功')

    # 創建使用者資料夾
    create_user_folder(user.id)
    print('創建使用者資料夾成功')

    return 201, {
        'id': user.id,
        'email': user.email,
    }


@router.post(
    path='login/',
    response={201: dict},
    summary='使用者登入',
    auth=None,
)
def login_user(request: HttpRequest, payload: LoginRequest) -> tuple[int, dict]:
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
    return 201, {
        'status': 'success',
        'access_token': access_token,
        'refresh_token': refresh_token,
    }


@router.post(
    path='logout/',
    response={200: dict},
    summary='使用者登出',
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
    path='jwt-token/refresh/',
    response={200: dict},
    summary='刷新 token',
    auth=None,
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


@router.post(
    path='verify-email/',
    response={200: dict},
    summary='信箱驗證信',
    auth=None,
)
def verify_email(request: HttpRequest, payload: VerifyEmailRequest) -> dict[str, str]:
    """
    信箱驗證信
    """
    # 解碼 token
    email = EmailVerificationService.verify_token(payload.active_token)
    user = User.objects.filter(email=email).first()

    # 若找不到使用者
    if not user:
        raise HttpError(400, '找不到該使用者')

    user.is_active = True
    user.save()
    return {
        'status': 'success',
        'message': '驗證成功',
    }


@router.post(
    path='update/{int:user_id}/avatar/',
    response={200: dict},
    summary='更新使用者頭像',
)
def update_avatar(
    request: HttpRequest, user_id: int, file: UploadedFile = File()
) -> tuple[int, dict]:
    """
    更新使用者頭像
    """

    if user_id != request.auth.id:
        raise HttpError(403, '無權限更新其他使用者的頭像')

    # 取得用戶實例
    user = request.auth

    # 獲取舊頭像的絕對路徑
    old_avatar_path = None
    if user.avatar:
        old_avatar_path = Path(user.avatar.path)

    # 檢查檔案格式和大小
    valiad, error = is_valid_image(file)
    if not valiad:
        raise HttpError(400, error)

    # 重新命名檔案
    new_filename = rename_file(file.name)
    file_content = ContentFile(file.read(), name=new_filename)

    try:
        # 儲存用戶新頭像
        user.avatar.save(new_filename, file_content, save=True)
        print(f'使用者 {user_id} 的頭像已更新: {user.avatar.url}')

        # 利用路由, 刪除舊頭像
        if old_avatar_path and old_avatar_path.exists():
            old_avatar_path.unlink()
            print(f'刪除舊頭像: {old_avatar_path}')

    except OSError as e:
        raise HttpError(400, f'無法儲存頭像: {e}')

    return 200, {
        'status': 'success',
        'user_id': user.id,
        'avatar_url': user.avatar.url,
    }


@router.patch(
    path='update/{int:user_id}/info/',
    response={200: dict},
    summary='更新使用者資訊',
)
def update_user_info(
    request: HttpRequest, user_id: int, payload: UpdateUserInfoIn
) -> tuple[int, dict]:
    """
    更新使用者資訊
    """
    if user_id != request.auth.id:
        raise HttpError(403, '無權限更新其他使用者的資訊')

    user = request.auth

    try:
        # 更新使用者資訊
        user.username = payload.nickname
        user.save()
        print(f'使用者 {user_id} 的資訊已更新')
    except Exception as e:
        raise HttpError(400, f'無法更新使用者資訊: {e}')

    return 200, {
        'status': 'success',
        'user_id': user.id,
    }
