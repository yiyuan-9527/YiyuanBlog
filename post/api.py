from typing import List

from django.http import HttpRequest
from ninja import File, Router, UploadedFile
from ninja.errors import HttpError
from PIL import Image

from post.schemas import CreatePost

router = Router()

# 上傳圖片設定
ALLOWED_IMAGE_FORMATS = {'JPG', 'JPEG', 'PNG'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@router.post(
    path='/posts/',
    response={201: CreatePost},
    summary='新增文章',
)
def create_post(request: HttpRequest, payload: CreatePost) -> tuple[int, dict]:
    """
    新增文章
    """


@router.post(
    path='/posts/{int:post_id}/images/',
    summary='上傳圖片',
)
def upload_post_image(
    request: HttpRequest, post_id: int, post_images: List[UploadedFile] = File()
) -> tuple[int, dict]:
    """
    上傳圖片
    """
    image_urls = []
    for image in post_images:
        # 檢查檔案大小
        if image.size > MAX_FILE_SIZE:
            raise HttpError(400, '請上傳小於20MB的圖片')

        # 使用 Pillow 開啟圖片並檢查格式
        try:
            image = Image.open(image.file)
        except Exception:
            raise HttpError(400, '無效的圖片檔案')

        # if image.format.
