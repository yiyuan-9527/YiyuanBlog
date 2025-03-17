from django.contrib.auth.models import AbstractUser
from django.db import models


# 自定義的 User 模型, 繼承自 AbstractUser
class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)  # 強制唯一的 username
    email = models.EmailField(unique=True)  # 強制唯一的 email
    password = models.CharField(max_length=128)  # 強制密碼長度
    bio = models.TextField(null=True)  # 個人簡介欄位（可選）
    avatar = models.ImageField(upload_to='avatars/', null=True)

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
        return self.username


# 追蹤 (Flollow) 模型
class Follow(models.Model):
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
