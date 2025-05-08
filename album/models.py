from datetime import datetime

from django.core.validators import FileExtensionValidator
from django.db import models

from user.models import User


class Album(models.Model):
    name = models.CharField(max_length=100, default='新增相簿名稱')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


# 儲存路徑設置
def album_image_path(instance: models.Model, filename: str) -> str:
    """
    圖片儲存路徑
    """
    user_id = str(instance.album.author.id)
    date = datetime.now().strftime('%Y/%m')

    return f'user_{user_id}/album_images/{date}/{filename}'


class AlbumImage(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=album_image_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
        ],
    )
    is_cover = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
