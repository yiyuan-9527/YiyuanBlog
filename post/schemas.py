from datetime import datetime
from typing import Any, Dict, List

from ninja import Field, Schema

from .models import Post


class _AuthorInfo(Schema):
    """
    作者資訊
    """

    id: int = Field(examples=[1])
    username: str | None = Field(examples=['Alice'])
    # email: str = Field(examples=['alice@example.com'])
    avatar_url: str | None = Field(examples=['https://example.com/avatar.jpg'])


class PostListOut(Schema):
    """
    文章列表輸出
    """

    # 欲新增 post_id, 重要！
    # 關聯的作者欄位
    author_name: str | None = Field(alias='author.username', examples=['寶淇'])
    author_avatar: str | None = Field(
        alias='author.avatar', examples=['https://example.com/avatar.jpg']
    )

    # 文章欄位
    id: int = Field(example=['1'])  # 文章ID
    updated_at: datetime = Field(examples=['2023-10-01T12:00:00Z'])
    title: str = Field(examples=['文章標題'])
    summery: str | None = Field(examples=['文章摘要'])  # 拼錯 是a 不是e
    thumbnail_url: str | None = Field(examples='https://example.com/thumbnail.jpg')

    @staticmethod
    def resolve_updated_at(obj: Post) -> str:
        return obj.updated_at.strftime('%Y-%m-%d')


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
    visibility: str = Field(examples=['public', 'private', 'followers', 'members'])


class GetPostDetailOut(Schema):
    """
    單篇文章內容輸出
    """

    id: int = Field(examples=[1])  # post id
    updated_at: datetime = Field(examples=['2025-07-29'])  # post updated time
    title: str = Field(examples=['文章標題'])
    content: Dict[str, Any] = Field(
        examples=[{'type': 'text', 'content': '文章的內容'}]
    )
    author: _AuthorInfo = Field(examples=['作者'])  # user_id, avatar, username
    followers: int = Field(examples=[2486])
    tags: List[str] = Field(default=[], examples=[['資料科學', '桌上遊戲']])
    like_count: int = Field(examples=[10])
    views_count: int = Field(examples=[100])


class BookmarkToggleOut(Schema):
    """
    切換收藏文章
    """

    is_bookmarked: bool = Field(examples=[True, False])
    bookmark_count: int = Field(examples=[10, 0])


class LikeStatusOut(Schema):
    """
    文章點讚狀態
    """

    is_liked: bool = Field(default=False, examples=['False=沒讚, True=已讚'])
    total_likes: int = Field(examples=['總讚數'])
