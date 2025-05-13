from django.utils import timezone

from .models import Storage

# def calculate_user_storage(user: object):
#     """
#     計算使用者的儲存空間

#     :param user: 使用者物件
#     :return: 使用了多少空間
#     """
#     total_bytes = 0

#     # 加總 PosttImage 檔案大小
#     post_images = PostImage.objects.filter(post__author=user)
#     total_bytes += sum(img.image.size for img in post_images if img.image)

#     # 加總 AlbumImage 檔案大小
#     album_images = AlbumImage.objects.filter(album__author=user)
#     total_bytes += sum(img.image.size for img in album_images if img.image)

#     return total_bytes


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
