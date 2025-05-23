from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from .models import Storage
from .schemas import UpgradePlanIn

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

    # 取得用戶使用了多少儲存空間
    used_bytes = user.storage_usage.used_storage
    # 計算用戶的儲存空間上限
    user_storage_limit = user.storage_usage.storage_limit
    print(user.storage_usage.storage_limit)

    return 200, {
        'status': 'success',
        'used_bytes': used_bytes,
        'storage_limit': round(
            user_storage_limit / (1024 * 1024), 2
        ),  # 轉換為 GB, 顯示小數點後兩位
        'used_gb': round(used_bytes / (1024 * 1024), 2),  # 轉換為 GB, 顯示小數點後兩位
    }


@router.post(
    path='upgrade/',
    response={200: dict},
    summary='升級方案',
)
def upgrade_plan(request: HttpRequest, payload: UpgradePlanIn) -> tuple[int, dict]:
    """
    升級用戶方案
    """
    user = request.auth
    storage = get_object_or_404(Storage, user=user)

    if payload.new_plan not in storage.PlanChoices.values:
        raise HttpError(400, '無效的方案')

    if storage.plan_name == payload.new_plan:
        raise HttpError(400, '已經是該方案了')

    # 升級邏輯
    if not storage.upgrade_to(payload.new_plan):
        raise HttpError(400, '升級方案失敗')

    return 200, {
        'status': 'success',
        'plan_name': storage.plan_name,
        'storage_limit': round(storage.storage_limit / (1024 * 1024 * 1024), 2),
        'plan_expire_at': storage.plan_expire_at,
    }
