from typing import List

from django.http import HttpRequest
from ninja import Router

from post.models import Post
from post.schemas import PostListOut

router = Router()


@router.get(
    path='homepage/test/',
    response=PostListOut,
    summary='首頁',
    auth=None,
)
def get_homepage_test(request: HttpRequest) -> PostListOut:
    post = Post.objects.first()
    return post


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

    # 根據建立時間取得文章列表，包含作者資訊
    posts = Post.objects.select_related('author').order_by('-created_at')[:6]
    print('返回首頁列表成功')
    return posts


@router.get(
    path='homepage/highlight/',
    response=List[PostListOut],
    summary='首頁精選文章列表',
    auth=None,
)
def get_homepage_highlight(request: HttpRequest) -> List[PostListOut]:
    """
    首頁精選文章列表
    """

    # 去掉沒有的縮圖文章
    # posts = Post.objects.select_related('author').filter(thumbnail_url__)
