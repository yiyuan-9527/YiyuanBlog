from typing import List

from django.db.models import Q
from django.http import HttpRequest
from ninja import Router

from post.models import Post
from post.schemas import PostListOut
from YiyuanBlog.auth import get_optional_user

from .service import PostService

router = Router()


@router.get(
    path='homepage/authtest/',
    response={200: dict},
    summary='首頁認證測試',
)
def homepage_auth_test(request: HttpRequest) -> tuple[int, dict]:
    """
    首頁認證測試
    """
    if request.auth:
        return 200, {
            'message': '已登入',
            'request.user 是誰': str(request.user),
            'request.auth 是誰': str(request.auth),
        }
    else:
        return 200, {'message': '未登入', '使用者': '訪客'}


@router.get(
    path='homepage/postlist/',
    response=List[PostListOut],
    summary='首頁文章列表',
    auth=None,
)
def get_homepage(request: HttpRequest) -> List[PostListOut]:
    """
    首頁文章列表
    """
    # 可選認證, 當前登入使用者
    user = get_optional_user(request)

    # 查詢文章列表, 預設是公開文章
    posts = PostService.get_homepage_posts(user=user)

    return posts


@router.get(
    path='homepage/highlight/',
    response=List[PostListOut],
    summary='首頁精選列表',
    auth=None,
)
def get_homepage_highlight(request: HttpRequest) -> List[PostListOut]:
    """
    首頁精選列表, 需要修改!!!!!
    """

    # 沒有縮圖文章不要上, filter 要加權限
    posts = (
        Post.objects.select_related('author')
        .filter(thumbnail_url__isnull=False)
        .order_by('?')[:12]
    )
    print('返回首頁精選列表成功')
    return posts
