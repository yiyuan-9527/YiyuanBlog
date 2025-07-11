from typing import List, Optional

from django.db.models import Q
from django.http import HttpRequest
from ninja import Depends, Router

from post.models import Post
from post.schemas import PostListOut
from user.models import Follow, User

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
def get_homepage(
    request: HttpRequest,
    user: Optional[User] = Depends,
) -> List[PostListOut]:
    """
    首頁文章列表
    """
    post_query = Post.objects.select_related('author').filter(status='published')

    # 權限邏輯: 檢查是否有認證
    if request.auth:
        # 已登入使用者: 根據權限過濾
        user = request.auth  # 這是當前認證的使用者

        conditions = Q(visibility='public') | Q(visibility='members')
        conditions |= Q(author=user)

        # 追蹤者權限
        followed_users = Follow.objects.filter(follower=user).values_list(
            'following', flat=True
        )
        conditions |= Q(visibility='followers', author__in=followed_users)

        posts_query = post_query.filter(conditions)
    else:
        # 未登入使用者: 只能看到公開文章
        posts_query = post_query.filterlter(visibility='public')

    posts = posts_query.order_by('-created_at')[:6]
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
