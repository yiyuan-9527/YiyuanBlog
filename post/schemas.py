from typing import List, Optional

from ninja import Field, Schema
from pydantic import HttpUrl


class CreatePost(Schema):
    """
    建立新文章的 Schema (傳遞圖片 URL)
    """

    title: str = Field(max_length=255, examples=['Post title'])
    content: str = Field(examples=['Post content'])
    # 使用 Optional 表示圖片是可選的
    # 這裡的 List[HttpUrl] 表示可以傳遞多個圖片 URL
    image_url: Optional[List[HttpUrl]] = Field(
        examples=['https://example.com/image.jpg']
    )
