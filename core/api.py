from typing import List

from django.http import HttpRequest
from ninja import Router

from post.models import Post
from post.schemas import PostListOut
from YiyuanBlog.auth import get_optional_user

from .service import PostService

router = Router()


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

    # 可選認證, 當前登入使用者
    user = get_optional_user(request)

    # 查詢精選文章列表, 預設是公開文章
    posts = PostService.get_highlight_posts(user=user)

    return posts
