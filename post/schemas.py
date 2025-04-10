from typing import List

from ninja import Field, Schema
from pydantic import HttpUrl

# class _AuthorInfo(Schema):
#     id: int = Field(examples=[1])
#     email: str = Field(examples=['test@example.com'])


class UpdatePostIn(Schema):
    """
    更新文章的請求
    """

    title: str | None = Field(
        default=None,
        max_length=255,
        examples=['title'],
    )
    content: str | None = Field(default=None, examples=['HTML content'])
    category_slug: str | None = Field(default=None, examples=['game'])
    tag_slugs: str | None = Field(default=None, examples=['tag1, tag2'])
    # 這裡的 List[HttpUrl] 表示可以傳遞多個圖片 URL
    image_url: List[HttpUrl] | None = Field(
        default=None,
        examples=[
            'https://example.com/image.jpg',
        ],
    )
