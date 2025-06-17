from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from post.models import (
    Post,
)

from .models import Comment
from .schemas import (
    CommentIn,
    CommentReplyOut,
)

router = Router()


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
    response={200: dict},
    summary='編輯留言',
)
def edit_comment(
    request: HttpRequest, comment_id: int, payload: CommentIn
) -> tuple[int, dict]:
    """
    編輯留言
    """
    