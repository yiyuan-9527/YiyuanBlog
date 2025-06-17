from ninja import NinjaAPI

from .auth import JWTAuth

api = NinjaAPI(
    auth=JWTAuth(),  # 設定全域認證
    title='YiyuanBlog API',
    version='0.0.1',
    description='這是一個 YiyuanBlog 的 API 文件, 供讀者參考',
)

# API 端點 endpoint
api.add_router(prefix='user/', router='user.api.router', tags=['User'])
api.add_router(prefix='post/', router='post.api.router', tags=['Post'])
api.add_router(prefix='album/', router='album.api.router', tags=['Album'])
api.add_router(prefix='storage/', router='storage.api.router', tags=['Storage'])
api.add_router(prefix='comment/', router='comment.api.router', tags=['Comment'])
api.add_router(prefix='/', router='core.api.router', tags=['Core'])
