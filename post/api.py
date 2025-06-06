from typing import List

from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import File, Router, UploadedFile
from ninja.errors import HttpError

from post.models import (
    Post,
    PostImage,
    PostVideo,
)
from post.schemas import (
    UpdatePostContentIn,
    UpdatePostTagIn,
)
from post.utils import (
    update_post_tags,
)
from shared.images_utils import (
    is_valid_image,
    is_valid_video,
    rename_file,
)
from storage.services import StorageService

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
@transaction.atomic  # 此 api 有原子性
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
    summary='文章上傳圖片',
)
def upload_test_image(  # files 是前端請求的 key, 這裡要對應
    request: HttpRequest, post_id: int, files: List[UploadedFile] = File()
) -> tuple[int, dict]:
    """
    上傳圖片
    檔案限制: jpg, jpeg, png
    大小限制: 3MB
    """
    post = get_object_or_404(Post, id=post_id)

    saved_files = []

    for file in files:
        # 驗證圖片格式和大小
        vaild, error = is_valid_image(file)
        if not vaild:
            raise HttpError(400, error)

        new_filename = rename_file(file.name)

        try:
            image_file = ContentFile(file.read(), name=new_filename)

            # 將圖片存至資料庫
            post_image = PostImage.objects.create(
                post=post,
                image=image_file,  # 檔案上傳的路徑在 models.py 裡面定義
                is_cover=False,  # 是否為封面圖片
            )

            # 設定 URL, 方便前端取得
            # post_image 實例. image 欄位. url 屬性
            file_url = request.build_absolute_uri(post_image.image.url)
            saved_files.append(file_url)

        except Exception as e:
            raise HttpError(400, f'無法儲存檔案: {e}')

    return 201, {
        'status': 'success',
        'file_name': saved_files,
    }


@router.post(
    path='upload/{int:post_id}/videos/',
    response={200: dict},
    summary='文章上傳影片',
)
@transaction.atomic
def upload_test_video(
    request: HttpRequest, post_id: int, files: List[UploadedFile] = File()
) -> tuple[int, dict]:
    """
    上傳影片
    檔案限制: mp4
    大小限制: 500MB
    """
    user = request.auth
    print('上傳影片的使用者:', user)
    post = get_object_or_404(Post, id=post_id)

    saved_files = []

    # 檢查使用者空間是否足夠
    total_upload_size = sum(file.size for file in files)
    user_space = StorageService.check_user_limit(user, total_upload_size)
    if not user_space:
        StorageService.exceeded_storage_limit(user)

    # 處理上傳的影片
    saved_files = []
    for file in files:
        # 驗證影片格式和大小
        valid, error = is_valid_video(file)
        if not valid:
            raise HttpError(400, error)

        # 重新命名
        new_filename = rename_file(file.name)
        video_file = ContentFile(file.read(), name=new_filename)

        try:
            # 將影片存至資料庫
            post_video = PostVideo.objects.create(
                post=post,
                video=video_file,
            )

            # 設定 URL, 方便前端取得
            file_url = request.build_absolute_uri(post_video.video.url)
            saved_files.append(file_url)

        except Exception as e:
            raise HttpError(400, f'無法儲存檔案: {e}')

        # 更新使用者儲存空間
        StorageService.add_item_storage(user, total_upload_size)

    return 200, {
        'status': 'success',
        'post_id': post.id,
        'file_urls': saved_files,
    }
