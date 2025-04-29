from django.utils import timezone

from .models import Storage


def upgrade_storage_plan(user, new_plan: str, duration_days: int = 30):
    """
    升級使用者的儲存方案

    :param user: 使用者物件
    :param new_plan: 新的方案名稱 (應符合 StorageUsage.PlanChoices)
    :param duration_days: 有效天數(預設為 30 天)
    """
    usage, created = Storage.objects.get_or_create(user=user)

    usage.plan_name = new_plan
    usage.is_paid = new_plan != Storage.PlanChoices.FREE
    usage.plan_expite_at = timezone.now() + timezone.timedelta(days=duration_days)

    # 自動更新 storage_limit (根據 save() 的邏輯)
    usage.storage_limit = usage.PlAN_STORAGE_LIMIT.get(new_plan, usage.storage_limit)

    usage.save()
    return usage
