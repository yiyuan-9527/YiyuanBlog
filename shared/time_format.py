from datetime import datetime

from django.utils import timezone as django_timezone


def to_readable(dt: datetime) -> str:
    """
    將時間格式轉換為人類易讀文字
    文章, 留言
    - dt: 要顯示的時間
    """

    # 取得現在時間
    now = django_timezone.now()

    # 確保都是有時區資訊的 datetime
    if dt.tzinfo is None:
        dt = django_timezone.make_aware(dt)

    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return '剛剛'

    elif seconds < 3600:  # 1小時內
        minuties = int(seconds // 60)
        return f'{minuties}分鐘前'

    elif seconds < 86400:  # 1天內
        hours = int(seconds // 3600)
        return f'{hours}小時前'

    elif seconds < 2592000:  # 30天內
        days = int(seconds // 86400)
        return f'{days}天前'

    elif seconds < 31536000:  # 1年內
        months = int(seconds // 2592000)
        return f'{months}個月前'

    else:
        years = int(seconds // 31536000)
        return f'{years}年前'
