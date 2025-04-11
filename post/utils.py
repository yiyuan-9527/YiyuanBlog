import re
import unicodedata
import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from ninja import UploadedFile
from ninja.errors import HttpError
from PIL import Image

# 上傳圖片設定
ALLOWED_IMAGE_FORMATS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def slugify(text: str) -> str:
    """
    將文字轉換為 slug 格式
    """
    # 將字串轉乘小寫
    text = text.lower()

    # 移除特殊字元(保留空格和中英文)
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', text)

    # 將空格替換為連字號
    text = re.sub(r'\s+', '-', text)

    # 去除線後多餘的連字號
    return text.strip('-')


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
