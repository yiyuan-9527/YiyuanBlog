from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import File, Router, UploadedFile
from ninja.errors import HttpError

from album.models import Album
from album.schemas import UpdateAlbumIn

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

    return 201, {'status': 'success', 'album_id': album.id}


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

    return 201, {'status': 'success', 'album_id': album.id}


@router.post(
    path='upload/{int:album_id}/',
    response={201: dict},
    summary='上傳相片',
)
def upload_album_image(
    request: HttpRequest, album_id: int, image: List[UploadedFile] = File()
) -> tuple[int, dict]:
    """
    上傳相片
    """
