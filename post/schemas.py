from typing import List

from ninja import Field, Schema
from pydantic import HttpUrl

# class _AuthorInfo(Schema):
#     id: int = Field(examples=[1])
#     email: str = Field(examples=['test@example.com'])


class UpdatePostContentIn(Schema):
    """
    更新文章內容
    """

    title: str | None = Field(
        default=None,
        max_length=255,
        examples=['title'],
    )
    content: str | None = Field(default=None, examples=['HTML content'])
    # 這裡的 List[HttpUrl] 表示可以傳遞多個圖片 URL
    image_url: List[HttpUrl] | None = Field(
        default=None,
        examples=[
            'https://example.com/image.jpg',
        ],
    )


class UpdatePostTagIn(Schema):
    """
    更新文章標籤分類
    """

    category_slug: str | None = Field(default=None, examples=['game'])
    tag_slugs: str | None = Field(default=None, examples=['tag1, tag2'])
