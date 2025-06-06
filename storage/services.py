from ninja.errors import HttpError

from user.models import User

from .models import Storage


class StorageService:
    @staticmethod
    def check_user_limit(user: User, total_file_size: int) -> bool:
        """
        檢查使用者的儲存空間是否已滿
        :param user: 使用者物件
        :return: True 如果已滿，否則 False
        """
        storage = Storage.objects.get(user=user)
        remaining_space = storage.storage_limit - storage.used_storage
        return remaining_space >= total_file_size

    @staticmethod
    def exceeded_storage_limit(user: User):
        """
        若儲存空間已滿, 拋出錯誤, 方便在 API 中捕捉
        """
        raise HttpError(413, f'使用者 {user.username} 的儲存空間已滿')

    @staticmethod
    def add_item_storage(user: User, total_file_size: int):
        """
        上傳檔案時, 更新使用者的儲存空間
        """
        storage = Storage.objects.get(user=user)
        storage.used_storage += total_file_size
        storage.save()
        print(f'上傳空間更新OK: {storage.used_storage}')

    @staticmethod
    def delete_item_storage(user: User, total_file_size: int):
        """
        刪除檔案時, 更新使用者的儲存空間
        """
        storage = Storage.objects.get(user=user)
        storage.used_storage -= total_file_size
        storage.save()
        print(f'刪除空間更新OK: {storage.used_storage}')
