from datetime import datetime
from typing import Any, Dict, List

from ninja import Field, Schema

# from .models import Post


class _AuthorInfo(Schema):
    """
    作者資訊
    """

    id: int = Field(examples=[1])
    username: str | None = Field(examples=['Alice'])
    email: str = Field(examples=['alice@example.com'])
    avatar_url: str | None = Field(examples=['https://example.com/avatar.jpg'])


class PostListOut(Schema):
    """
    文章列表輸出
    """

    # 關聯的作者欄位
    author_name: str | None = Field(examples=['寶淇'])
    author_avatar: str | None = Field(examples=['https://example.com/avatar.jpg'])

    # 文章欄位
    updated_at: datetime = Field(examples=['2023-10-01T12:00:00Z'])
    title: str = Field(examples=['文章標題'])
    summery: str | None = Field(examples=['文章摘要'])  # 拼錯 是a 不是e
    thumbnail_url: str | None = Field(examples='https://example.com/thumbnail.jpg')

    # @staticmethod
    # def resolve_author_name(obj: Post) -> str:
    #     return obj.author.username or obj.author.email

    # @staticmethod
    # def resolve_author_avatar(obj: Post) -> str | None:
    #     return obj.author.avatar.url if obj.author.avatar.url else None

    # @staticmethod
    # def resolve_updated_at(obj: Post) -> str:
    #     return obj.updated_at.strftime('%Y-%m-%d')


class UpdatePostContentIn(Schema):
    """
    更新文章內容
    """

    title: str | None = Field(default=None, max_length=255, examples=['title'])
    content: Dict[str, Any] | None = Field(
        default=None,
        examples={
            'type': 'doc',
            'content': [
                {
                    'type': 'paragraph',
                    'content': [
                        {
                            'type': 'text',
                            'text': '文章內容',
                        },
                    ],
                }
            ],
        },
    )


class UpdatePostTagIn(Schema):
    """
    更新分類、標籤
    """

    # category_slug: str | None = Field(default=None, examples=['game'])
    tags: List[str] | None = Field(default=None, examples=[['資料科學', '桌上遊戲']])


class PostDetailOut(Schema):
    """
    單篇文章內容輸出
    """

    id: int = Field(examples=[1])
    title: str = Field(examples=['文章標題'])
    content: Dict[str, Any] = Field(
        examples=[{'type': 'text', 'content': '文章的內容'}]
    )
    author: _AuthorInfo = Field(examples=['作者'])
    category: str | None = Field(default=None, examples=['分類名稱'])
    tags: List[str] = Field(default=[], examples=[['資料科學', '桌上遊戲']])
    created_at: str = Field(examples=['2023-10-01T12:00:00Z'])
    updated_at: str = Field(examples=['2023-10-01T12:00:00Z'])
    status: str = Field(examples=['draft', 'published', 'private'])
