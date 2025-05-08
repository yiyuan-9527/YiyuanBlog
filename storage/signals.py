from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Storage


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_storage(sender: object, instance: object, created: bool, **kwargs):
    """
    當使用者註冊時，建立對應的儲存空間紀錄
    :param sender: 發送信號的模型類別
    """
    if created:
        Storage.objects.create(user=instance)
        print(f'儲存空間建立OK: {instance.email}')
