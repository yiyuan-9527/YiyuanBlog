from django.http import HttpRequest
from ninja import Router

from post.models import Post
from post.schemas import PostListOut

from .schemas import HomePageOut

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
    path='homepage/',
    response={200: HomePageOut},
    summary='首頁',
    auth=None,
)
def get_homepage(request: HttpRequest) -> tuple[int, HomePageOut]:
    """
    首頁
    """
    # 假設有登入的話

    # 取得文章清單
    posts_queryset = Post.objects.order_by('-created_at')[:6].select_related('author')
    #  把 QuerySet 轉換成 PostListOut 的列表
    posts_data = [PostListOut.from_orm(post) for post in posts_queryset]

    # return 巢狀 JSON
    return 200, HomePageOut(
        posts=posts_data,
    )
