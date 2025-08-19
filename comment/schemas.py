from datetime import datetime
from typing import List

from ninja import Field, Schema

from shared.time_format import to_readable


class CommentIn(Schema):
    content: str = Field(examples=['留言內容'])
    parent_id: int | None = Field(default=None, description='父留言的 id', examples=[1])


class CommentReplyOut(Schema):
    id: int
    content: str = Field(examples=['我要成為海賊王'])
    author: str = Field(examples=['蒙奇 D 魯夫'])
    create_at: datetime = Field(examples=['2025-06-16'])
    likes_count: int = Field(default=0, examples=[1])
    parent_id: int | None = Field(description='父留言的 id', examples=[])


class CommentEditOut(Schema):
    content: str = Field(examples=['我要成為海賊王'])
    updated_at: datetime = Field(examples=['2025-06-16'])
    is_edited: bool = Field(examples=['是否為編輯'])


class GetCommentOut(Schema):
    id: int
    content: str = Field(examples=['我要成為海賊王'])
    author: str = Field(examples=['蒙奇 D 魯夫'])
    updated_at: str = Field(examples=['5分鐘之前'])  # 時間格式經過處理, 是 str
    is_liked: bool = Field(examples=['False=沒讚, True=已讚'])
    likes_count: int = Field(default=0, examples=[1])
    parent_id: int | None = Field(default=None)
    is_edited: bool = Field(default=False)
    replies: List['GetCommentOut'] = Field(default_factory=list)

    @staticmethod
    def from_comment_recursive(comment, user=None):
        # 判斷當前使用者是否已讚這則留言
        is_liked = False
        if user:
            is_liked = comment.likes.filter(user=user).exists()

        return {
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username,
            'updated_at': to_readable(comment.updated_at),
            'is_liked': is_liked,
            'likes_count': getattr(comment, 'likes_count', comment.likes.count()),
            'parent_id': comment.parent.id if comment.parent else None,
            'is_edited': comment.created_at != comment.updated_at,
            'replies': [
                GetCommentOut.from_comment_recursive(reply, user)
                for reply in comment.replies.all()
            ],
        }


class LikeStatusOut(Schema):
    is_liked: bool = Field(default=False, examples=['False=沒讚, True=已讚'])
    total_likes: int = Field(examples=['總讚數'])
