from django.http import HttpRequest
from ninja import Router

from .utils import calculate_user_storage

router = Router()


@router.get(
    path='info/',
    response={200: dict},
    summary='取得使用者儲存空間資訊',
)
def get_storage_info(request: HttpRequest) -> tuple[int, dict]:
    """
    取得使用者儲存空間資訊
    """
    print(f'User: {request.auth}')
    user = request.auth
    used_bytes = calculate_user_storage(user)
    user_storage_limit = user.storage_usage.storage_limit

    return 200, {
        'status': 'success',
        'used_bytes': used_bytes,
        'storage_limit': round(
            user_storage_limit / (1024 * 1024 * 1024), 2
        ),  # 轉換為 GB, 顯示小數點後兩位
        'used_gb': round(
            used_bytes / (1024 * 1024 * 1024), 2
        ),  # 轉換為 GB, 顯示小數點後兩位
    }
