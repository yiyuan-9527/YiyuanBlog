from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from album.models import AlbumImage

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


@receiver(post_save, sender=AlbumImage)
def add_item_storage(sender: object, instance: object, created: bool, **kwargs):
    """
    當圖片上傳時, 更新使用者的儲存空間
    """
    if created:
        user = instance.album.user
        file_size = instance.image.size

        storage = user.storage_usage  # 取得當前容量
        storage.used_storage += file_size
        storage.save()
        print(f'儲存空間更新OK: {storage.used_storage}')


@receiver(post_delete, sender=AlbumImage)
def delete_item_storage(sender: object, instance: object, **kwargs):
    """
    當圖片刪除時, 更新使用者的儲存空間
    """
    user = instance.album.user
    file_size = instance.image.size

    storage = user.storage_usage  # 取得當前容量
    storage.used_storage -= file_size
    storage.save()
    print(f'儲存空間更新OK: {storage.used_storage}')
