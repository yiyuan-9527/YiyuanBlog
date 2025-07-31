from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Count, Prefetch
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import File, Router, UploadedFile
from ninja.errors import HttpError

from post.models import (
    Bookmark,
    Post,
    PostImage,
    PostVideo,
    TagManagement,
)
from post.schemas import (
    BookmarkToggleOut,
    GetPostDetailOut,
    LikeStatusOut,
    UpdatePostContentIn,
    UpdatePostTagIn,
    _AuthorInfo,
)
from post.services import ProseMirrorContentExtrator
from post.utils import (
    update_post_tags,
)
from shared.images_utils import (
    is_valid_image,
    is_valid_video,
    rename_file,
)
from storage.services import StorageService
from user.models import Follow
from YiyuanBlog.auth import get_optional_user

from .services import GetPostService

router = Router()


@router.get(
    path='{int:post_id}/',
    response=GetPostDetailOut,
    summary='查詢單篇文章內容',
    auth=None,
)
def get_post_detail(request: HttpRequest, post_id: int) -> GetPostDetailOut:
    """
    查詢單篇文章內容
    """
    # 可選認證, 當前登入使用者
    user = get_optional_user(request)

    # 使用 select_related 和 prefetch_related 優化查詢
    try:
        post = (
            Post.objects.select_related('author')
            .prefetch_related(
                'tags',
                'likes',
                Prefetch(
                    'tagmanagement_set',
                    queryset=TagManagement.objects.select_related('tag'),
                ),
            )
            .get(id=post_id, status='published')
        )
    except Post.DoesNotExist:
        raise HttpError(404, '文章不存在或尚未發布')

    # 檢查文章可見性權限
    if not GetPostService._check_post_visibility(post, user=user):
        raise HttpError(404, '無權限查看此文章')

    # 增加瀏覽次數
    post.views_count += 1
    post.save(update_fields=['views_count'])

    # 計算作者的追蹤者數量
    followers_count = Follow.objects.filter(following=post.author).count()

    # 計算文章案讚數
    like_count = post.likes.count()

    # 取得文章標籤
    tags = [tag_mgmt.tag.name for tag_mgmt in post.tagmanagement_set.all()]

    # 組裝回應資料
    return GetPostDetailOut(
        id=post.id,
        updated_at=post.updated_at,
        title=post.title,
        content=post.content,
        author=_AuthorInfo(
            id=post.author.id,
            username=post.author.username,
            avatar_url=post.author.avatar.url if post.author.avatar else None,
        ),
        followers=followers_count,
        tags=tags,
        like_count=like_count,
        views_count=post.views_count,
    )


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


@router.patch(
    path='update/{int:post_id}/',
    response={200: dict},
    summary='即時更新文章',
)
def upload_post(
    request: HttpRequest, post_id: int, payload: UpdatePostContentIn
) -> tuple[int, dict]:
    """
    即時更新文章
    """

    # 取得指定文章
    try:
        post = get_object_or_404(Post, id=post_id)
    except Post.DoesNotExist:
        raise HttpError(404, '文章不存在')

    # 權限檢查
    if post.author != request.auth:
        raise HttpError(403, '無權限修改此文章')

    # 更新文章
    # 迭代 payload 的屬性, 將其值設置到 post 物件上
    for attr, value in payload.dict().items():
        setattr(post, attr, value)
    post.save()
    print(f'文章及時更新成功: {post.title}')

    return 200, {
        'status': 'success',
        'post_id': post.id,
    }


@router.patch(
    path='finish/{int:post_id}/',
    response={200: dict},
    summary='發布文章',
)
@transaction.atomic  # 此 api 有原子性
def post_article(
    request: HttpRequest, post_id: int, payload: UpdatePostTagIn
) -> tuple[int, dict]:
    """
    發布文章, 更新標籤. 設定文章權限. 產生摘要. 縮圖
    """
    post = get_object_or_404(Post, id=post_id)

    # 權限檢查
    if post.author != request.auth:
        raise HttpError(403, '無權限修改此文章')

    # 標籤不為空的話, 更新文章標籤
    if payload.tags is not None:
        update_post_tags(post, payload.tags)

    # 傳入 visibility, 設定文章可見權限
    if payload.visibility is not None:
        post.visibility = payload.visibility

    # 更改文章狀態為已發布
    post.status = 'published'

    # 產生文章摘要和縮圖
    if post.content is not None:
        extracted_summary = ProseMirrorContentExtrator.extract_plain_text(post.content)
        extracted_thumnail_url = ProseMirrorContentExtrator.extract_first_image_url(
            post.content
        )
        post.summery = extracted_summary[:200]  # 限制摘要長度為 200 字
        post.thumbnail_url = extracted_thumnail_url
    post.save()

    print(f'文章發布成功: {post.title}')

    return 200, {
        'status': 'success',
        'post_id': post.id,
    }


@router.post(
    path='upload/{int:post_id}/images/',
    response={200: dict},
    summary='文章上傳圖片',
)
def upload_test_image(  # files 是前端請求的 key, 這裡要對應
    request: HttpRequest, post_id: int, file: UploadedFile = File()
) -> tuple[int, dict]:
    """
    上傳圖片
    檔案限制: jpg, jpeg, png
    大小限制: 3MB
    """
    user = request.auth
    post = get_object_or_404(Post, id=post_id)

    # 檢查使用者空間是否足夠
    user_space = StorageService.check_user_limit(user, file.size)
    if not user_space:
        StorageService.exceeded_storage_limit(user)

    # 處理上傳的照片
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

    except Exception as e:
        raise HttpError(400, f'無法儲存檔案: {e}')

    # 更新使用者儲存空間
    StorageService.add_item_storage(user, file.size)

    return 200, {
        'status': 'success',
        'post_id': post.id,
        'file_url': file_url,
    }


@router.post(
    path='upload/{int:post_id}/videos/',
    response={200: dict},
    summary='文章上傳影片',
)
@transaction.atomic
def upload_test_video(
    request: HttpRequest, post_id: int, file: UploadedFile = File()
) -> tuple[int, dict]:
    """
    上傳影片
    檔案限制: mp4
    大小限制: 500MB
    """
    user = request.auth
    print('上傳影片的使用者:', user)
    post = get_object_or_404(Post, id=post_id)

    # 檢查使用者空間是否足夠
    user_space = StorageService.check_user_limit(user, file.size)
    if not user_space:
        StorageService.exceeded_storage_limit(user)

    # 處理上傳的影片
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

    except Exception as e:
        raise HttpError(400, f'無法儲存檔案: {e}')

    # 更新使用者儲存空間
    StorageService.add_item_storage(user, file.size)

    return 200, {
        'status': 'success',
        'post_id': post.id,
        'file_url': file_url,
    }


@router.post(
    path='like/toggle/{int:post_id}/',
    response={200: LikeStatusOut},
    summary='切換文章點讚狀態',
)
def toggle_post_like(request: HttpRequest, post_id: int) -> tuple[int, LikeStatusOut]:
    """
    - 如果用戶尚未對文章點讚, 新增底讚
    - 反之取消點讚
    """
    user = request.auth
    post = get_object_or_404(Post, id=post_id)

    with transaction.atomic():
        like_obj, created = post.likes.get_or_create(
            user=user,
            post=post,
        )

        if created:
            # 新增點讚
            is_liked = True
            print(f'{user.username}點讚')
        else:
            # 取消讚
            like_obj.delete()
            is_liked = False
            print(f'{user.username}收回讚')

        # 重新計算總讚數
        total_likes = post.likes.count()
        print(f'總讚數: {total_likes}')

    return 200, {
        'is_liked': is_liked,
        'total_likes': total_likes,
    }


@router.delete(
    path='delete/{int:post_id}/',
    response={200: dict},
    summary='刪除文章',
)
def delete_post(request: HttpRequest, post_id: int) -> tuple[int, dict]:
    """
    刪除文章
    """
    post = get_object_or_404(Post, id=post_id)

    # 權限檢查
    if post.author != request.auth:
        raise HttpError(403, '無權限刪除此文章')

    # 刪除文章
    post.delete()
    print(f'文章已刪除: {post.title}')

    return 200, {'status': 'success'}


# =========== 收藏文章 ===========
@router.post(
    path='bookmark/toggle/{int:post_id}/',
    response=BookmarkToggleOut,
    summary='收藏或取消收藏文章',
)
def toggle_bookmark(request: HttpRequest, post_id: int) -> BookmarkToggleOut:
    """
    切換文章收藏狀態
    - 如果尚未收藏, 則收藏文章
    - 反之就取消收藏
    """
    user = request.auth
    post = get_object_or_404(Post, id=post_id)

    with transaction.atomic():
        bookmark_obj, created = Bookmark.objects.get_or_create(
            user=user,
            post=post,
        )

        if created:
            # 收藏文章
            is_bookmarked = True
            print(f'使用者 {user.username} 收藏了文章: {post.title}')
        else:
            # 取消收藏文章
            bookmark_obj.delete()
            is_bookmarked = False
            print(f'使用者 {user.username} 取消收藏了文章: {post.title}')

        # 重新計算收藏數
        bookmark_count = post.bookmarked_by.count()

    return {
        'is_bookmarked': is_bookmarked,
        'bookmark_count': bookmark_count,
    }
