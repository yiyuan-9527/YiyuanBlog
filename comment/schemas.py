from datetime import datetime

from ninja import Field, Schema


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
