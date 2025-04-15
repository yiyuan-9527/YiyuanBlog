import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from django.utils.text import slugify
from ninja import UploadedFile
from ninja.errors import HttpError
from PIL import Image

from post.models import Post, Tag, TagManagement

# 上傳圖片設定
ALLOWED_IMAGE_FORMATS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def get_or_create_tag(tag_text: str) -> Tag:
    """
    根據 tag 名稱取得或建立 Tag 物件
    """
    slug = slugify(tag_text, allow_unicode=True)
    tag, created = Tag.objects.get_or_create(
        slug=slug,
        defaults={'name': tag_text},
    )

    # 如果標籤名稱與 slug 不同，則更新標籤名稱
    # 若有找到 = False 且標籤名稱不同，則更新標籤名稱
    if not created and tag.name != tag_text:
        tag.name = tag_text
        tag.save()
    return tag


def update_post_tags(post: Post, tag_list: list[str]) -> None:
    """
    清除原有標籤, 並根據給定 tag list 更新文章標籤
    """
    # 清除現有標籤
    TagManagement.objects.filter(post=post).delete()

    for tag_text in tag_list:
        tag = get_or_create_tag(tag_text)
        TagManagement.objects.create(post=post, tag=tag)


def is_valid_image(file: UploadedFile) -> tuple[bool, str]:
    """
    驗證圖片格式和大小
    """
    ext = file.name.split('.')[-1].lower()
    if ext not in ALLOWED_IMAGE_FORMATS:
        return False, '不支援的圖片格式, 請上傳 jpg, jpeg 或 png 格式的圖片'
    if file.size > MAX_FILE_SIZE:
        return False, '圖片大小超過 20MB, 請上傳小於 20MB 的圖片'

    return True, None


def process_image_to_webp(file: UploadedFile) -> ContentFile:
    """
    將圖片轉換為 WebP 格式
    在記憶體中(DRAM)處理圖片並返回 ContentFile, 不在硬碟上儲存
    """
    try:
        image = Image.open(file.file)
    except Exception as e:
        raise HttpError(400, f'無法處理圖片: {e}')

    image = image.convert('RGB')
    image_buffer = BytesIO()

    image.save(image_buffer, format='WEBP', quality=80)
    # 將指標移到緩衝區的開始位置
    image_buffer.seek(0)
    # 將圖片轉換為 WebP 格式並返回 ContentFile
    # 使用 UUID 生成唯一的檔案名稱
    # 這裡的 name 只是用於在 Django 中顯示檔案名稱，實際上不會儲存到硬碟
    return ContentFile(image_buffer.getvalue())


def generate_unique_filename() -> str:
    """
    生成唯一的檔案名稱
    """
    return f'{uuid.uuid4().hex}.webp'
