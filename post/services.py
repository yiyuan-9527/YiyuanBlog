from typing import Any, Dict, List


class ProseMirrorContentExtrator:
    @staticmethod
    def extract_plain_text(pm_json: Dict[str, Any]) -> str:
        """
        從 ProseMirror JSON 結構中提取純文本內容
        """
        if not isinstance(pm_json, dict) or 'type' not in pm_json:
            return ''

        text_content = []

        def traverse_nodes(nodes: List[Dict[str, Any]]):
            for node in nodes:
                if node.get('type') == 'text' and 'text' in node:
                    text_content.append(node['text'])
                if 'content' in node:
                    traverse_nodes(node['content'])

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

        def traverse_nodes(nodes: List[Dict[str, Any]]):
            for node in nodes:
                if node.get('type') == 'image' and node.get('attrs', {}).get('scr'):
                    return node['attrs']['src']

                if 'content' in node:
                    result = traverse_nodes(node['content'])
                    if result:
                        return result

            return None

        if 'content' in pm_json:
            return traverse_nodes(pm_json('content'))

        return None
