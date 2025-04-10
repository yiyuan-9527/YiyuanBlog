from django.core.validators import FileExtensionValidator
from django.db import models

from user.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)


class Post(models.Model):
    title = models.CharField(max_length=255)  # 文章標題
    slug = models.SlugField(unique=True, null=True)  # 文章網址
    content = models.TextField()  # 文章內容
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 關聯到自定義 User 模型
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # 分類
    tags = models.ManyToManyField(Tag)  # 標籤
    created_at = models.DateTimeField(auto_now_add=True)  # 發文時間
    updated_at = models.DateTimeField(auto_now=True)  # 更新時間
    status = models.CharField(  # 狀態
        max_length=20,
        choices=[
            ('draft', '草稿'),
            ('published', '已發布'),
            ('private', '私密'),
        ],
        default='draft',
    )
    views_count = models.PositiveIntegerField(default=0)  # 瀏覽數量

    def __str__(self) -> str:
        return self.title


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='post_images/%Y/%m',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
        ],
        width_field='width',  # 指定儲存寬度的欄位名稱
        height_field='heidht',  # 指定儲存高度的欄位名稱
    )
    alt_text = models.CharField(max_length=100, blank=True)
    is_cover = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    width = models.PositiveIntegerField(null=True, blank=True)  # 用於儲存寬度的整數欄位
    height = models.PositiveIntegerField(
        null=True, blank=True
    )  # 用於儲存高度的整數欄位
