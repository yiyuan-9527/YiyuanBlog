from django.core.validators import FileExtensionValidator
from django.db import models

from user.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)


class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(
        Tag, through='TagManagement', through_fields=('post', 'tag')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', '草稿'),
            ('published', '已發布'),
            ('private', '私密'),
        ],
        default='draft',
    )
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.title


# Post 和 Tag 的中介表
class TagManagement(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


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
