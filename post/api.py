import os
from typing import List

from django.core.files.storage import default_storage
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import File, Router, UploadedFile
from ninja.errors import HttpError

from post.models import Post, PostImage
from post.schemas import UpdatePostIn
from post.utils import generate_unique_filename, is_valid_image, process_image_to_webp

router = Router()


@router.post(
    path='create/',
    response={201: dict},
    summary='新增文章',
)
def create_post(request: HttpRequest) -> tuple[int, dict]:
    """
    新增文章
    """
    # 解析 JWT token, 取得使用者資訊
    user = request.auth
    try:
        post = Post.objects.create(
            author=user,
        )
    except Exception as e:
        raise HttpError(400, f'無法建立文章: {e}')

    return 201, {'status': 'success', 'post_id': post.id}


@router.put(
    path='{int:post_id}/',
    response={201: dict},
    summary='更新文章',
)
def upload_post(
    request: HttpRequest, post_id: int, payload: UpdatePostIn
) -> tuple[int, dict]:
    """
    更新文章
    """
    # 取得指定文章
    try:
        post = get_object_or_404(Post, id=post_id)
    except Post.DoesNotExist:
        raise HttpError(404, '文章不存在')

    # 更新文章
    # 迭代 payload 的屬性, 將其值設置到 post 物件上
    for attr, value in payload.dict().items():
        setattr(post, attr, value)
    post.save()
    return 201, {'status': 'success', 'post_id': post.id}


@router.post(
    path='{int:post_id}/images/',
    response={201: dict},
    summary='上傳圖片',
)
def upload_post_image(
    request: HttpRequest, post_id: int, files: List[UploadedFile] = File()
) -> tuple[int, dict]:
    """
    接收多個圖片檔案, 依序驗證格式和大小,
    建立對應的 PostImage 物件並儲存到資料庫
    回傳圖片 URL list
    """
    # 取得指定文章
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise HttpError(404, '文章不存在')

    # 儲存圖片 URL list
    image_urls = []
    for file in files:
        # 驗證圖片格式和大小
        valid, error = is_valid_image(file)
        if not valid:
            raise HttpError(400, error)

        # 將圖片轉換為 WebP 格式
        try:
            image_content = process_image_to_webp(file)
        except HttpError as e:
            raise HttpError(400, f'無法處理圖片: {e}')

        # 產生唯一檔名與儲存路徑 ( 放到 media/post_images/)
        unique_filename = generate_unique_filename()
        upload_path = os.path.join('post_images', unique_filename)

        # 儲存圖片檔案
        saved_path = default_storage.save(upload_path, image_content)

        # 儲存圖片到資料庫
        PostImage.objects.create(
            post=post,
            image=image_content,
            alt_text=file.name,
            is_cover=False,
        )

        # 產生 URL, 方便前端取得
        image_url = request.build_absolute_uri(f'/media/{saved_path}')
        image_urls.append(image_url)

    return 201, {'image_urls': image_urls}
