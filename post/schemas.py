from typing import Any, Dict, List

from ninja import Field, Schema
from pydantic import HttpUrl


class _AuthorInfo(Schema):
    """
    作者資訊
    """

    id: int = Field(examples=[1])
    username: str = Field(examples=['Alice'])
    email: str = Field(examples=['alice@example.com'])


class UpdatePostContentIn(Schema):
    """
    更新文章內容
    """

    title: str | None = Field(default=None, max_length=255, examples=['title'])
    content: Dict[str, Any] | None = Field(default=None, examples=['HTML content'])
    summary: str | None = Field(examples=['文章摘要'])
    # 這裡的 List[HttpUrl] 表示可以傳遞多個圖片 URL
    image_url: List[HttpUrl] | None = Field(
        default=None,
        examples=[
            'https://example.com/image.jpg',
        ],
    )


class UpdatePostTagIn(Schema):
    """
    更新文章標籤, 分類
    """

    # category_slug: str | None = Field(default=None, examples=['game'])
    tags: List[str] | None = Field(default=None, examples=[['資料科學', '桌上遊戲']])


class PostDetailOut(Schema):
    """
    文章內容輸出
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


class PostListOut(Schema):
    """
    文章列表輸出
    """

    id: int = Field(examples=[1])
    author: _AuthorInfo = Field(examples=['作者'])
    title: str = Field(examples=['文章標題'])
    summary: str | None = Field(examples=['文章摘要'])
    thumbnail_url: str | None = Field(examples='https://example.com/thumbnail.jpg')
