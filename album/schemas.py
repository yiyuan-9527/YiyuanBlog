from typing import List

from ninja import Field, Schema


class UpdateAlbumIn(Schema):
    """
    更新相簿
    """

    name: str | None = Field(max_length=255, examples=['相簿名稱'])


class DeleteAlbumImageIn(Schema):
    """
    刪除相簿圖片
    """

    images_id: List[int] = Field(examples=[[1, 2, 3]])
