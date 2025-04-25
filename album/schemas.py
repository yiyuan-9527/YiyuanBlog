from ninja import Field, Schema


class UpdateAlbumIn(Schema):
    """
    更新相簿
    """

    name: str | None = Field(max_length=255, examples=['相簿名稱'])
