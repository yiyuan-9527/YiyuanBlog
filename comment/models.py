# from django.db import models


# class Comment(models.Model):
#     post = models.ForeignKey(
#         'post.Post',
#         on_delete=models.CASCADE,
#         related_name='comments',
#     )
#     author = models.ForeignKey('user.User', on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     parent = models.ForeignKey(
#         'self',
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         related_name='replies',
#     )  # 巢狀留言
