import mimetypes
import uuid
from pathlib import Path

from ninja import UploadedFile

# 上傳圖片限制
ALLOWED_IMAGE_FORMATS = {'image/jpeg', 'image/jpg', 'image/png'}
MAX_FILE_SIZE = 3 * 1024 * 1024
# 上傳影片限制
ALLOWED_VIDEO_FORMATS = {'video/mp4'}
MAX_VIDEO_SIZE = 1024 * 1024 * 500  # 500MB


def is_valid_image(file: UploadedFile) -> tuple[bool, str]:
    """
    驗證圖片格式和大小
    """
    mime_type, _ = mimetypes.guess_type(file.name)

    if mime_type is None or not mime_type.startswith('image/'):
        return False, '不支援的圖片格式, 請上傳 jpg, jpeg, png 格式的圖片'
    if mime_type not in ALLOWED_IMAGE_FORMATS:
        return (
            False,
            f'不支援的圖片格式: {mime_type}, 請上傳 jpg, jpeg, png 格式的圖片',
        )
    if file.size > MAX_FILE_SIZE:
        return False, f'{file.name}大小超過 3MB, 請上傳小於 3MB 的圖片'

    return True, None


def is_valid_video(file: UploadedFile) -> tuple[bool, str]:
    """
    驗證影片格式和大小
    """
    mime_type, _ = mimetypes.guess_type(file.name)

    if mime_type is None or not mime_type.startswith('video/'):
        return False, '不支援的影片格式, 請上傳 mp4 格式的影片'
    if mime_type not in ALLOWED_VIDEO_FORMATS:
        return (
            False,
            f'不支援的影片格式: {mime_type}, 請上傳 mp4 格式的影片',
        )
    if file.size > MAX_VIDEO_SIZE:
        return False, f'{file.name}大小超過 500MB, 請上傳小於 500MB 的影片'

    return True, None


def rename_file(original_filename: str) -> str:
    """
    根據原檔名產生不重複的新檔名
    格式: 原檔名_UUID4.副檔名
    """
    # 檔案名稱,不包含副檔名
    original_stem = Path(original_filename).stem

    # 副檔名
    original_suffix = Path(original_filename).suffix

    unique_filename = uuid.uuid4().hex[:8]  # 可調整長度, 只用前8碼
    new_filename = f'{original_stem}_{unique_filename}{original_suffix}'

    return new_filename


# 棄用
# def process_image_to_webp(file: UploadedFile) -> tuple[str, bytes]:
#     """
#     將圖片轉換為 WebP 格式, 在記憶體中(DRAM)處理圖片
#     """
#     # 檔案名稱,不包含副檔名
#     original_stem = Path(file.name).stem
#     # 產生不重複的檔名
#     unique_name = rename_file(original_stem + '.webp')

#     try:
#         image = Image.open(file)
#     except Exception as e:
#         raise HttpError(400, f'無法處理圖片: {e}')

#     image = image.convert('RGB')
#     # 建立記憶體的暫存物件
#     buffer = BytesIO()
#     # 將圖片存進記憶體的暫存物件, 並轉換為 WebP 格式
#     image.save(buffer, format='WEBP', quality=80)
#     # 返回 名稱, 暫存物件的內容
#     return unique_name, buffer.getvalue()
