from django.db import models


class Comment(models.Model):
    """
    留言
    """

    post = models.ForeignKey(
        'post.Post',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField()
    # 巢狀留言
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author.username} 在 {self.post.title} 留言'


class Like(models.Model):
    """
    有夠讚
    """

    user = models.ForeginKey('User', on_delete=models.CASCADE)
    comment = models.ForeginKey(
        'Comment', on_delete=models.CASCADE, related_name='likes'
    )
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f'{self.user.username} 喜歡這篇文章 {self.comment.id}'
