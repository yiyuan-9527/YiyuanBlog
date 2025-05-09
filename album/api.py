from pathlib import Path
from typing import List

from django.core.files.base import ContentFile
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import File, Router, UploadedFile
from ninja.errors import HttpError

from album.models import (
    Album,
    AlbumImage,
)
from album.schemas import (
    DeleteAlbumImageIn,
    UpdateAlbumIn,
)
from shared.images_utils import (
    is_valid_image,
    process_image_to_webp,
)
from storage.services import StorageService

router = Router()


@router.post(
    path='create/',
    response={201: dict},
    summary='新增相簿',
)
def create_album(request: HttpRequest) -> tuple[int, dict]:
    """
    新增相簿
    """
    user = request.auth
    try:
        album = Album.objects.create(
            author=user,
        )
    except Exception as e:
        raise HttpError(400, f'無法建立相簿: {e}')

    return 201, {
        'status': 'success',
        'album_id': album.id,
    }


@router.put(
    path='update/{int:album_id}/',
    response={201: dict},
    summary='更新相簿名稱',
)
def upload_album(
    request: HttpRequest, album_id: int, payload: UpdateAlbumIn
) -> tuple[int, dict]:
    """
    更新相簿名稱
    """
    album = get_object_or_404(Album, id=album_id)

    # 更新相簿名稱
    album.name = payload.name
    album.save()
    print(f'更新相簿名稱: {album.name}')

    return 201, {
        'status': 'success',
        'album_id': album.id,
    }


@router.post(
    path='upload/{int:album_id}/',
    response={201: dict},
    summary='上傳相片',
)
def upload_album_image(
    request: HttpRequest, album_id: int, images: List[UploadedFile] = File()
) -> tuple[int, dict]:
    """
    上傳相片
    檔案限制: jpg, jpeg, png
    大小限制: 3MB
    """
    user = request.auth
    album = get_object_or_404(Album, id=album_id)

    # 檢查使用者空間是否足夠
    total_upload_size = sum(image.size for image in images)
    user_space = StorageService.check_user_limit(user, total_upload_size)
    if not user_space:
        StorageService.exceeded_storage_limit(user)

    # 開始處理上傳的圖片
    saved_images = []
    for image in images:
        # 驗證圖片格式和大小
        vaild, error = is_valid_image(image)
        if not vaild:
            raise HttpError(400, error)

        new_filename, webp_bytes = process_image_to_webp(image)

        try:
            image_file = ContentFile(webp_bytes, name=new_filename)

            # 將相片存至資料庫
            album_image = AlbumImage.objects.create(
                album=album,
                image=image_file,
            )

            file_url = request.build_absolute_uri(album_image.image.url)
            saved_images.append(file_url)

        except Exception as e:
            raise HttpError(400, f'無法儲存檔案: {e}')

    return 201, {
        'status': 'success',
        'album_id': album.id,
        'images': saved_images,
    }


@router.delete(
    path='delete/{int:album_id}/image/',
    response={201: dict},
    summary='刪除相片',
)
def delete_album_image(
    request: HttpRequest, album_id: int, payload: DeleteAlbumImageIn
) -> tuple[int, dict]:
    """
    刪除相片
    """
    album = get_object_or_404(Album, id=album_id)

    if album.author != request.auth:
        raise HttpError(403, '無權限刪除此相片')

    for image_id in payload.images_id:
        try:
            image = get_object_or_404(AlbumImage, id=image_id)

            # 找到相片路徑並刪除
            image_path = Path(image.image.path)
            if image_path.exists():
                image_path.unlink()

            # 刪除資料庫路徑
            image.delete()
        except Exception as e:
            raise HttpError(400, f'無法刪除檔案: {e}')

    return 201, {
        'status': 'success',
        'album_id': album.id,
    }
