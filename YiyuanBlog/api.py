from ninja import NinjaAPI

from .auth import JWTAuth

api = NinjaAPI(
    auth=JWTAuth(),  # 設定全域認證
    title='YiyuanBlog API',
    version='0.0.1',
    description='這是一個 YiyuanBlog 的 API 文件, 供讀者參考',
)

# API endpoints
api.add_router(prefix='', router='user.api.router', tags=['User'])
api.add_router(prefix='post/', router='post.api.router', tags=['Post'])
