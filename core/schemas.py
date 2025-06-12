from typing import List

from ninja import Field, Schema

from post.schemas import PostListOut


class HomePageOut(Schema):
    """
    首頁輸出
    """

    posts: List[PostListOut] = Field(examples=['文章列表'])
