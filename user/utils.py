from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from ninja.errors import HttpError

from .models import User


def create_user_folder(user_id: int) -> None:
    """
    創建使用者資料夾
    """
    # 設置路徑
    user_folder = Path(settings.MEDIA_ROOT) / f'user_{user_id}'
    try:
        user_folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        HttpError(500, f'創建使用者資料夾失敗: {e}')


class EmailVerificationService:
    @staticmethod
    def generate_verfication_token(user: User) -> str:
        """
        生成驗證 token
        """
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        active_token = serializer.dumps(user.email, salt='activate')
        return active_token

    @staticmethod
    def verify_token(active_token: str, max_age=3600) -> Any:  # 預設 1 小時過期
        """
        驗證 token
        """
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

        try:
            # max_age 參數控制 token 的有效時間(秒)
            email = serializer.loads(active_token, salt='activate', max_age=max_age)
            print('驗證信箱成功')
            return email
        except SignatureExpired:
            return {'error': '驗證連結已過期'}
        except BadSignature:
            return {'error': '驗證連結無效'}

    @staticmethod
    def send_verification_email(user: User):
        """
        發送驗證信
        """
        # 生成驗證 token
        active_token = EmailVerificationService.generate_verfication_token(user)
        print('驗證註冊Token: ', active_token)

        # url 後續改成前端的驗證頁面
        veurification_url = 'http://127.0.0.1:8000/api/users/verify-email/'
        subject = '驗證您的信箱'
        message = f'請點擊以下連結驗證您的信箱: {veurification_url}'

        # 發送驗證信
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
