import os
from pathlib import Path
from typing import List

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import File, Router, UploadedFile
from ninja.errors import HttpError

from post.models import (
    Post,
    PostImage,
)
from post.schemas import (
    UpdatePostContentIn,
    UpdatePostTagIn,
)
from post.utils import (
    generate_unique_filename,
    is_valid_image,
    process_image_to_webp,
    update_post_tags,
)

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
    # 解析 JWT token, 取得使用者資訊, 才知道是誰在發文
    user = request.auth
    try:
        post = Post.objects.create(
            author=user,
        )
    except Exception as e:
        raise HttpError(400, f'無法建立文章: {e}')

    return 201, {'status': 'success', 'post_id': post.id}


@router.put(
    path='update/{int:post_id}/',
    response={201: dict},
    summary='更新文章',
)
def upload_post(
    request: HttpRequest, post_id: int, payload: UpdatePostContentIn
) -> tuple[int, dict]:
    """
    更新文章內容
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
    print(f'更新成功: {post.title}')
    return 201, {'status': 'success', 'post_id': post.id}


@router.put(
    path='update/{int:post_id}/tags/',
    response={201: dict},
    summary='更新文章標籤',
)
@transaction.atomic
def upload_post_tags(
    request: HttpRequest, post_id: int, payload: UpdatePostTagIn
) -> tuple[int, dict]:
    """
    更新文章標籤
    """
    post = get_object_or_404(Post, id=post_id)

    # 權限檢查
    if post.author != request.auth:
        raise HttpError(403, '無權限修改此文章')

    if payload.tags is not None:
        update_post_tags(post, payload.tags)

    return 201, {'status': 'success', 'post_id': post.id}


@router.post(
    path='upload/{int:post_id}/images/',
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


@router.post(
    path='upload/image/test/',
    response={201: dict},
    summary='測試上傳圖片',
)
def upload_test_image(
    request: HttpRequest, files: List[UploadedFile] = File()
) -> tuple[int, dict]:
    """
    測試上傳圖片
    """
    saved_files = []
    for file in files:
        # 驗證圖片格式和大小
        vaild, error = is_valid_image(file)
        if not vaild:
            raise HttpError(400, error)

        file_path = Path(settings.MEDIA_ROOT) / file.name
        try:
            with open(file_path, 'wb+') as f:
                file_content = file.read()
                f.write(file_content)
            saved_files.append(file.name)

        except Exception as e:
            raise HttpError(400, f'無法儲存檔案: {e}')

    return 201, {
        'status': 'success',
        'file_name': saved_files,
    }
