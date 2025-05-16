from datetime import datetime, timedelta, timezone

from django.db import models
from enum import Enum
from user.models import User

class TEST(Enum):
    QQQ = 'qqq','免費方案'


class Storage(models.Model):
    class PlanChoices(models.TextChoices):
        FREE = 'Free', '免費方案'
        BASIC = 'BASIC', '基本方案'
        STANDARD = 'STANDARD', '標準方案'
        PREMIUM = 'PREMIUM', '高級方案'

    PLAN_STORAGE_LIMIT = {
        PlanChoices.FREE: 1024 * 1024 * 1024 * 50,  # 50 GB
        PlanChoices.BASIC: 1024 * 1024 * 1024 * 150,  # 150 GB
        PlanChoices.STANDARD: 1024 * 1024 * 1024 * 300,  # 300 GB
        PlanChoices.PREMIUM: 1024 * 1024 * 1024 * 800,  # 800 GB
    }

    user = models.OneToOneField(  # 使用者
        User, on_delete=models.CASCADE, related_name='storage_usage'
    )
    used_storage = models.BigIntegerField(default=0)  # 已使用的儲存空間
    storage_limit = models.BigIntegerField(blank=True)  # 儲存空間上限
    is_paid = models.BooleanField(default=False)  # 是否為付費會員, 可刪除
    plan_name = models.CharField(  # 方案名稱
        max_length=10,
        choices=PlanChoices.choices,
        default=PlanChoices.FREE,
    )
    plan_expire_at = models.DateTimeField(
        null=True, blank=True
    )  # 付費到期時間(免費用戶為空)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Storage Usage"

    def save(self, *args, **kwargs):
        """
        預設儲存空間上限
        """
        if not self.storage_limit:
            self.storage_limit = self.PLAN_STORAGE_LIMIT.get(self.plan_name, 0)
        super().save(*args, **kwargs)

    def upgrade_to(self, new_plan: str):
        """
        升級方案
        :param plan_name: 方案名稱
        """
        if new_plan in self.PlanChoices.values:
            self.plan_name = new_plan
            self.storage_limit = self.PLAN_STORAGE_LIMIT.get(new_plan, 0)
            self.plan_expire_at = datetime.now(timezone.utc) + timedelta(minutes=3)
            self.is_paid = True
            self.save()
            return True
        return False
