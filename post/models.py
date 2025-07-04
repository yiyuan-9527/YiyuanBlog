from datetime import datetime

from django.core.validators import FileExtensionValidator
from django.db import models

from user.models import User


# 分類模型 未啟用!
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self) -> str:
        return self.name


# 標籤模型
class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self) -> str:
        return self.name


# Post 和 Tag 的中介表
class TagManagement(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.post.title} - {self.tag.name}'


# 文章模型
class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True)
    content = models.JSONField(
        default=dict,
        help_text='文章內容, 可以是 HTML 或其他格式的內容',
    )

    summery = models.TextField(  # 拼錯, 是a 不是e
        blank=True,
        null=True,
        help_text='文章摘要, 用於 SEO 或文章列表顯示',
    )
    thumbnail_url = models.URLField(
        max_length=1800,
        blank=True,
        null=True,
        help_text='文章縮圖 URL, 用於文章列表或社交媒體分享',
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(
        Tag, through='TagManagement', through_fields=('post', 'tag')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(  # 文章發布狀態
        max_length=20,
        choices=[
            ('draft', '草稿'),
            ('published', '已發布'),
        ],
        default='draft',
    )
    visibility = models.CharField(  # 文章可見性
        max_length=50,
        choices=[
            ('public', '開放所有人'),
            ('private', '只限本人'),
            ('followers', ' 只限追蹤者'),
            ('members', '只限會員'),
        ],
        default='public',
    )
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.title


class Like(models.Model):
    """
    讚
    """

    user = models.ForeignKey(
        'user.User', on_delete=models.CASCADE, related_name='liked_posts'
    )
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self) -> str:
        return f'{self.user.username} 喜歡這篇文章 {self.post.title}'


def post_image_path(instance: models, filename: str) -> str:
    """
    圖片儲存路徑
    """
    # 物件的 post 欄位;的 author 欄位;的 id 欄位
    user_id = str(instance.post.author.id)
    date = datetime.now().strftime('%Y/%m')

    return f'user_{user_id}/post_images/{date}/{filename}'


# 文章內的圖片
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=post_image_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
        ],
    )
    is_cover = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)


def post_video_path(instance: models, filename: str) -> str:
    user_id = str(instance.post.author.id)
    date = datetime.now().strftime('%Y/%m')

    return f'user_{user_id}/post_videos/{date}/{filename}'


# 文章內的影片
class PostVideo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    video = models.FileField(
        upload_to=post_video_path,
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)


# =========== 收藏文章 ===========
# 收藏模型
class Bookmark(models.Model):
    user = models.ForeignKey(
        'user.User', on_delete=models.CASCADE, related_name='bookmarks'
    )
    post = models.ForeignKey(
        'post.Post', on_delete=models.CASCADE, related_name='bookmarked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:  # 影響 model migration 的唯一性約束
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.username} 收藏了 {self.post.title}'
 