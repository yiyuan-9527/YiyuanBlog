from typing import List

from django.db import transaction
from django.db.models import Count
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from post.models import (
    Post,
)
from YiyuanBlog.auth import get_optional_user

from .models import Comment, Like
from .schemas import (
    CommentEditOut,
    CommentIn,
    CommentReplyOut,
    GetCommentOut,
    LikeStatusOut,
)

router = Router()


@router.get(
    path='get/{int:post_id}/',
    response={200: List[GetCommentOut]},
    summary='查詢留言',
    auth=None,
)
def get_comment(request: HttpRequest, post_id: int) -> tuple[int:List]:
    """
    查詢留言
    """
    # 可選認證, 當前登入使用者
    user = get_optional_user(request)

    top_level_comments = (
        Comment.objects.filter(
            post=post_id,
            parent__isnull=True,
        )
        .prefetch_related(
            'replies__replies__replies',
            'likes',  # 預載入點讚資料
            'replies__likes',  # 預載入回覆的點讚資料
            'replies__replies__likes',
        )
        .annotate(
            likes_count=Count('likes')  # 用 annotation 計算讚數，避免重複查詢
        )
    )

    return 200, [
        GetCommentOut.from_comment_recursive(comment, user)
        for comment in top_level_comments
    ]


@router.post(
    path='create/{int:post_id}/',
    response={200: CommentReplyOut},
    summary='新增留言',
)
def create_new_reply(
    request: HttpRequest, post_id: int, payload: CommentIn
) -> tuple[int, dict]:
    """
    新增留言
    """
    post = get_object_or_404(Post, id=post_id)

    # 如果是回覆留言, 驗證父留言存在且屬於同一篇文章
    parent_comment = None
    if payload.parent_id:
        parent_comment = get_object_or_404(
            Comment,
            id=payload.parent_id,
            post=post,
        )

    # 建立留言
    comment = Comment.objects.create(
        post=post,
        author=request.auth,
        content=payload.content,
        parent=parent_comment,
    )
    print(f'回覆留言成功: {comment.author}')
    return 200, {
        'id': comment.id,
        'content': comment.content,
        'author': comment.author.username,
        'create_at': comment.created_at,
        'likes_count': 0,
        'parent_id': parent_comment.id if parent_comment else None,
    }


@router.patch(
    path='edit/{int:comment_id}/',
    response={200: CommentEditOut},
    summary='編輯留言',
)
def edit_comment(
    request: HttpRequest, comment_id: int, payload: CommentIn
) -> tuple[int, CommentEditOut]:
    """
    編輯留言
    """

    # 找到該留言
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.auth:
        raise HttpError(403, '沒有權限編輯留言')

    if not payload.content.strip():
        raise HttpError(400, '內容不能為空')

    # 更新新留言
    comment.content = payload.content
    comment.save(update_fields=['content'])
    print(f'編輯留言成功:{comment.id}')

    return 200, {
        'content': comment.content,
        'updated_at': comment.updated_at,
        'is_edited': comment.is_edited,
    }


@router.delete(
    path='delete/{int:comment_id}/',
    response={200: dict},
    summary='刪除留言',
)
def delete_comment(request: HttpRequest, comment_id: int) -> tuple[int, dict]:
    """
    刪除留言
    """

    # 找到該留言
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.auth:
        raise HttpError(403, '沒有權限刪除留言')

    # 刪除留言
    comment.delete()
    print('刪除留言成功')

    return 200, {
        'status': 'success',
    }


@router.post(
    path='like/toggle/{int:comment_id}/',
    response={200: LikeStatusOut},
    summary='切換留言點讚狀態',
)
def toggle_comment_like(
    request: HttpRequest, comment_id: int
) -> tuple[int, LikeStatusOut]:
    """
    - 如果用戶尚未對留言點讚, 新增點讚
    - 反之取消點讚
    """
    user = request.auth
    comment = get_object_or_404(Comment, id=comment_id)

    with transaction.atomic():
        like_obj, created = Like.objects.get_or_create(
            user=user,
            comment=comment,
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
        total_likes = comment.likes.count()
        print(f'總讚數: {total_likes}')

    return 200, {
        'is_liked': is_liked,
        'total_likes': total_likes,
    }
