from typing import Any, Dict, List

from django.contrib.auth.models import AbstractUser

from post.models import Post
from user.models import Follow


class ProseMirrorContentExtrator:
    @staticmethod
    def extract_plain_text(pm_json: Dict[str, Any]) -> str:
        """
        從 ProseMirror JSON 結構中提取純文本內容
        """
        if not isinstance(pm_json, dict) or 'type' not in pm_json:
            return ''

        text_content = []

        # 遞迴遍歷 ProseMirror JSON 結構中的節點
        def traverse_nodes(nodes: List[Dict[str, Any]]):
            for node in nodes:
                if node.get('type') == 'text' and 'text' in node:
                    text_content.append(node['text'])
                if 'content' in node:
                    traverse_nodes(node['content'])

        # 遞迴入口
        if 'content' in pm_json:
            traverse_nodes(pm_json['content'])

        return ''.join(text_content).strip()

    @staticmethod
    def extract_first_image_url(pm_json: Dict[str, Any]) -> str:
        """
        從 ProseMirror JSON 結構中提取第一個圖片 URL
        假設圖片節點的 type 為 'image' 且 URL 在 attrs.src 中
        """
        if not isinstance(pm_json, dict) or 'type' not in pm_json:
            return None

        # 遞迴遍歷 ProseMirror JSON 結構中的節點
        def traverse_nodes(nodes: List[Dict[str, Any]]):
            for node in nodes:
                if node.get('type') == 'image' and node.get('attrs', {}).get('src'):
                    print(f'找到圖片 URL: {node["attrs"]["src"]}')
                    return node['attrs']['src']

                if 'content' in node:
                    result = traverse_nodes(node['content'])

                    # 如果在子節點中找到圖片 URL, 才會跑到這裡
                    # 若在父節點中找到圖片 URL, 則不會進入這個 if
                    if result:
                        print(f'從子層接收到結果，向上返回: {result}')
                        return result

            # 如果結果不是 None, 則返回結果
            print('沒有找到圖片 URL')
            return None

        # 遞迴入口
        if 'content' in pm_json:
            return traverse_nodes(pm_json['content'])

        return None


class GetPostService:
    @staticmethod
    def _check_post_visibility(post: Post, user: AbstractUser | None = None) -> bool:
        """
        檢查文章的可見性
        """
        # 公開文章所有人都可以看
        if post.visibility == 'public':
            return True

        # 未登入用戶只能看公開文章
        if not user:
            return False

        # 作者本人可以看自己的文章
        if post.author == user:
            return True

        # 私人文章只有作者可以看
        if post.visibility == 'private':
            return False

        # 只限追蹤者的文章
        if post.visibility == 'followers':
            return Follow.objects.filter(
                follower=user,
                following=post.author,
            ).exists()

        # 只限會員的文章(已登入即可)
        if post.visibility == 'members':
            return True

        return False


def get_post_list(limit: int = 10) -> List[Dict[str, Any]]:
    """
    獲取文章列表
    """
    return (
        Post.objects.filter(status='published')
        .select_related('author')
        .order_by('-updated_at;')[:limit]
    )
