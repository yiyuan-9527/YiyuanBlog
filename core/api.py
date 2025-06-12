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

    # 取得文章清單
    posts_queryset = Post.objects.select_related('author').order_by('-created_at')[:6]
    #  把 QuerySet 轉換成 PostListOut 的列表
    # posts_data = [PostListOut.from_orm(post) for post in posts_queryset]
    posts_data = []
    for post in posts_queryset:
        post_data = PostListOut(
            author_name=post.author.username or post.author.email,
            author_avatar=post.author.avatar.url if post.author.avatar else None,
            updated_at=post.updated_at.strftime('%Y-%m-%d'),
            title=post.title,
            summery=post.summery,  # 拼錯 是a 不是e
            thumbnail_url=post.thumbnail_url,
        )
        posts_data.append(post_data)

    # print(f'posts_data 內容: {posts_data}')

    # return 巢狀 JSON
    return 200, HomePageOut(
        posts=posts_data,
    )
