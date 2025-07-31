from django.contrib.auth.models import AbstractUser
from django.db.models import Q, QuerySet

from post.models import Post
from user.models import Follow


class PostService:
    """
    文章業務邏輯
    """

    @staticmethod
    def get_homepage_posts(
        user: AbstractUser | None = None, limit: int = 6
    ) -> QuerySet[Post]:
        """
        獲取首頁文章列表
        :param user: 當前登入使用者, 如果沒有登入則為 None
        :param limit: 限制返回的文章數量
        """
        # 基礎查詢: 只查詢公開文章
        base_query = Post.objects.select_related('author').filter(status='published')

        if user:
            # 已登入使用者的文章可見性條件
            conditions = PostService._get_auth_user_conditions(user)
            filtered_query = base_query.filter(conditions)
            print(f'使用者: {user} 已登入, 根據權限過濾文章')

        else:
            # 未登入使用者只能看公開文章
            filtered_query = base_query.filter(visibility='public')
            print('未登入使用者, 只能看到公開文章')

        return filtered_query.order_by('-created_at')[:limit]

    @staticmethod
    def get_highlight_posts(
        user: AbstractUser | None = None, limit: int = 12
    ) -> QuerySet[Post]:
        """
        獲取首頁精選文章列表
        :param user: 當前登入使用者, 如果沒有登入則為 None
        :param limit: 限制返回的精選文章數量
        """
        # 基礎查詢: 只查詢公開文章
        #  沒有縮圖文章不要上, filter 要加權限
        base_query = Post.objects.select_related('author').filter(
            status='published', thumbnail_url__isnull=False
        )

        if user:
            # 已登入使用者的文章可見性條件
            conditions = PostService._get_auth_user_conditions(user)
            filtered_query = base_query.filter(conditions)
            print(f'使用者: {user} 已登入, 根據權限過濾精選文章')

        else:
            # 未登入使用者只能看公開文章
            filtered_query = base_query.filter(visibility='public')
            print('未登入使用者, 只能看到公開精選文章')

        return filtered_query.order_by('?')[:limit]

    @staticmethod
    def _get_auth_user_conditions(user: AbstractUser) -> Q:
        """
        獲取已登入使用者的文章可見性條件
        :param user: 當前登入使用者
        """
        # 公開文章和會員文章
        conditions = Q(visibility='public') | Q(visibility='members')
        # 自己的文章
        conditions |= Q(author=user)

        # 追蹤者可見的文章
        followed_users = Follow.objects.filter(follower=user).values_list(
            'following', flat=True
        )
        conditions |= Q(visibility='followers', author__in=followed_users)

        return conditions
