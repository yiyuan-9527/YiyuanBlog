from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models


# 頭像上傳路徑設置
def avatar_upload_path(instance: models.Model, filename: str) -> str:
    """
    頭像圖片儲存路徑
    """
    user_id = str(instance.id)

    return f'user_{user_id}/avatar/{filename}'


# 自定義的 User 模型, 繼承自 AbstractUser
class User(AbstractUser):
    username = models.CharField(max_length=150, unique=False, null=True)
    email = models.EmailField(unique=True)  # 強制唯一的 email
    password = models.CharField(max_length=128)  # 強制密碼長度
    bio = models.TextField(null=True)  # 個人簡介欄位（可選）
    avatar = models.ImageField(  # 頭像圖片欄位
        upload_to=avatar_upload_path,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    )
    is_active = models.BooleanField(default=False)  # 信箱驗證欄

    USERNAME_FIELD = 'email'  # 使用 email 作為登入的識別欄位
    REQUIRED_FIELDS = []  # 讓 email 變成唯一身份欄位

    # 設置不同的 related_name 來避免與 Django 預設模型發生衝突
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # 自定義 related_name 避免衝突
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # 自定義 related_name 避免衝突
        blank=True,
    )

    def __str__(self) -> str:
        return self.email


# 追蹤 (Flollow) 模型
class Follow(models.Model):
    # related_name 是反向關係, 兩個欄位容易混淆
    follower = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='following_relations'
    )
    following = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='follower_relations'
    )

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'{self.follower.username} → {self.following.username}'
